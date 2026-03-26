from flask import Blueprint, current_app, jsonify, request
import logging
import re
import hashlib
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone
from pymongo.errors import PyMongoError

from ..services.company_service import CompanyService
from ..services.email_service import EmailService
from ..services.auth_service import generate_token
from ..utils.validators import validate_company_registration
from ..utils.auth_middleware import require_auth
from ..utils.email_queue import enqueue_or_send

company_bp = Blueprint("company", __name__)
logger = logging.getLogger(__name__)
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso_datetime(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed
    except (TypeError, ValueError):
        return None


def _request_ip() -> str:
    forwarded_for = (request.headers.get("X-Forwarded-For") or "").strip()
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return (request.remote_addr or "").strip()


def _rate_limit_key(scope: str, email: str, ip_address: str) -> str:
    normalized_email = (email or "").strip().lower()
    base = f"{scope}:{ip_address}" if scope == "ip" else f"{scope}:{ip_address}:{normalized_email}"
    digest = hashlib.sha256(base.encode("utf-8")).hexdigest()
    return f"{scope}:{digest}"


def _consume_rate_limit_bucket(
    collection,
    *,
    key: str,
    max_attempts: int,
    window_minutes: int,
    ip_address: str,
    user_agent: str,
) -> tuple[bool, int]:
    now = _utc_now()
    doc = collection.find_one({"_id": key})
    window_delta = timedelta(minutes=max(1, window_minutes))

    if not doc:
        collection.update_one(
            {"_id": key},
            {
                "$set": {
                    "attemptCount": 1,
                    "windowStartedAt": now.isoformat(),
                    "windowEndsAt": (now + window_delta).isoformat(),
                    "lastAttemptAt": now.isoformat(),
                    "ipAddress": ip_address,
                    "userAgent": (user_agent or "")[:255],
                }
            },
            upsert=True,
        )
        return False, 0

    window_ends_at = _parse_iso_datetime(doc.get("windowEndsAt", ""))
    if not window_ends_at or now > window_ends_at:
        collection.update_one(
            {"_id": key},
            {
                "$set": {
                    "attemptCount": 1,
                    "windowStartedAt": now.isoformat(),
                    "windowEndsAt": (now + window_delta).isoformat(),
                    "lastAttemptAt": now.isoformat(),
                    "ipAddress": ip_address,
                    "userAgent": (user_agent or "")[:255],
                }
            },
            upsert=True,
        )
        return False, 0

    attempt_count = int(doc.get("attemptCount", 0))
    if attempt_count >= max(1, max_attempts):
        retry_after_seconds = max(1, int((window_ends_at - now).total_seconds()))
        return True, retry_after_seconds

    collection.update_one(
        {"_id": key},
        {
            "$inc": {"attemptCount": 1},
            "$set": {
                "lastAttemptAt": now.isoformat(),
                "ipAddress": ip_address,
                "userAgent": (user_agent or "")[:255],
            },
        },
    )
    return False, 0


def _check_forgot_password_rate_limit(db, email: str, ip_address: str, user_agent: str) -> tuple[bool, int]:
    collection = db["password_reset_rate_limits"]
    window_minutes = int(current_app.config["PASSWORD_RESET_RATE_LIMIT_WINDOW_MINUTES"])
    max_email_ip = int(current_app.config["PASSWORD_RESET_RATE_LIMIT_MAX_ATTEMPTS_PER_EMAIL_IP"])
    max_ip = int(current_app.config["PASSWORD_RESET_RATE_LIMIT_MAX_ATTEMPTS_PER_IP"])

    ip_limited, ip_retry = _consume_rate_limit_bucket(
        collection,
        key=_rate_limit_key("ip", email, ip_address),
        max_attempts=max_ip,
        window_minutes=window_minutes,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    if ip_limited:
        return True, ip_retry

    email_ip_limited, email_ip_retry = _consume_rate_limit_bucket(
        collection,
        key=_rate_limit_key("email-ip", email, ip_address),
        max_attempts=max_email_ip,
        window_minutes=window_minutes,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return email_ip_limited, email_ip_retry


def _resolve_frontend_base_url(payload: dict) -> str:
    """Resolve frontend base URL from request payload with safe fallback to config."""
    fallback = (current_app.config.get("FRONTEND_BASE_URL") or "http://localhost:5173").strip()
    fallback_parsed = urlparse(fallback)
    candidate = (payload.get("frontendBaseUrl") or "").strip()
    if not candidate:
        fallback_host = (fallback_parsed.hostname or "").lower()
        request_host = (request.host.split(":")[0] if request.host else "").strip().lower()
        if fallback_host in {"localhost", "127.0.0.1"} and request_host not in {"", "localhost", "127.0.0.1"}:
            scheme = fallback_parsed.scheme or request.scheme or "http"
            port = fallback_parsed.port or 5173
            return f"{scheme}://{request_host}:{port}"
        return fallback

    try:
        parsed = urlparse(candidate)
    except Exception:
        return fallback

    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return fallback

    return f"{parsed.scheme}://{parsed.netloc}"


def _verify_captcha(token: str) -> bool:
    """
    Verify a reCAPTCHA v2 client token against Google's API.

    Returns True when:
    - RECAPTCHA_SECRET_KEY is not configured (CAPTCHA disabled)
    - OR the token passes Google's verification

    Returns False when:
    - RECAPTCHA_SECRET_KEY is configured but the token is missing or invalid
    """
    secret = (current_app.config.get("RECAPTCHA_SECRET_KEY") or "").strip()
    if not secret:
        return True  # CAPTCHA not configured — skip silently

    if not token:
        return False

    try:
        import urllib.request
        import urllib.parse
        import json as _json
        verify_url = current_app.config.get("RECAPTCHA_VERIFY_URL", "https://www.google.com/recaptcha/api/siteverify")
        data = urllib.parse.urlencode({"secret": secret, "response": token}).encode()
        with urllib.request.urlopen(verify_url, data, timeout=5) as resp:
            result = _json.loads(resp.read())
        return bool(result.get("success"))
    except Exception as exc:
        logger.warning("CAPTCHA verification error (%s) — treating as failed", exc)
        return False


def _resolve_production_base_url(payload: dict) -> str:
    """
    Like ``_resolve_frontend_base_url`` but also honours ``APP_DOMAIN`` for
    production deployments where a real domain (e.g. https://app.company.com)
    should be used instead of the LAN IP.
    """
    app_domain = (current_app.config.get("APP_DOMAIN") or "").strip().rstrip("/")
    if app_domain:
        parsed = urlparse(app_domain)
        if parsed.scheme in {"http", "https"} and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}"
    return _resolve_frontend_base_url(payload)


@company_bp.route("/company/register", methods=["POST"])
def register_company():
    try:
        payload = request.get_json(silent=True) or {}

        # S5: Input validation
        validation_errors = validate_company_registration(payload)
        if validation_errors:
            return jsonify({"success": False, "message": "; ".join(validation_errors)}), 400

        service = CompanyService(current_app.mongo_db)
        result = service.register_company(
            company_name=payload["companyName"],
            registration_no=payload["registrationNo"],
            email=payload["email"],
            password=payload["password"],
            score_threshold=float(payload.get("scoreThreshold", current_app.config.get("SCORE_THRESHOLD", 70))),
        )

        if not result.get("success"):
            logger.warning("Registration failed: %s", result.get("message"))
            return jsonify(result), 400

        # A1: Issue token so user is logged in immediately after registration
        token = generate_token(result["company"]["companyId"], current_app.config["SECRET_KEY"])
        result["token"] = token
        logger.info("Company registered: %s", payload["email"])
        return jsonify(result), 200

    except PyMongoError:
        logger.exception("Registration DB error")
        return jsonify({"success": False, "message": "Database unavailable. Please try again shortly."}), 503
    except Exception:
        logger.exception("Registration error")
        # S3: Never expose internal exception text to client
        return jsonify({"success": False, "message": "Registration failed due to a server error"}), 500


@company_bp.route("/company/login", methods=["POST"])
def login_company():
    try:
        payload = request.get_json(silent=True) or {}
        if not payload.get("email") or not payload.get("password"):
            return jsonify({"success": False, "message": "Email and password required"}), 400

        service = CompanyService(current_app.mongo_db)
        result = service.login_company(payload["email"], payload["password"])

        if not result.get("success"):
            logger.warning("Login failed for email: %s", payload.get("email"))
            return jsonify(result), 401

        # A1: Issue a signed JWT on successful login
        token = generate_token(result["company"]["companyId"], current_app.config["SECRET_KEY"])
        result["token"] = token
        logger.info("Company logged in: %s", payload["email"])
        return jsonify(result), 200

    except PyMongoError:
        logger.exception("Login DB error")
        return jsonify({"success": False, "message": "Database unavailable. Please try again shortly."}), 503
    except Exception:
        logger.exception("Login error")
        # S3: Never expose internal exception text to client
        return jsonify({"success": False, "message": "Login failed due to a server error"}), 500


@company_bp.route("/company/forgot-password", methods=["POST"])
def request_password_reset():
    """Send password reset link email (generic response to prevent account enumeration)."""
    try:
        payload = request.get_json(silent=True) or {}
        email = (payload.get("email") or "").strip().lower()
        frontend_base_url = _resolve_production_base_url(payload)
        requester_ip = _request_ip()
        user_agent = (request.headers.get("User-Agent") or "").strip()
        if not email or not _EMAIL_RE.match(email):
            return jsonify({"success": False, "message": "A valid email is required"}), 400

        # ── CAPTCHA verification (optional — skipped when not configured) ─────
        captcha_token = (payload.get("captchaToken") or "").strip()
        if not _verify_captcha(captcha_token):
            return jsonify({"success": False, "message": "CAPTCHA verification failed. Please try again."}), 400

        service = CompanyService(current_app.mongo_db)
        is_limited, retry_after_seconds = _check_forgot_password_rate_limit(
            current_app.mongo_db,
            email,
            requester_ip,
            user_agent,
        )
        if is_limited:
            service.log_password_reset_audit(
                event="password_reset_requested",
                outcome="rate-limited",
                email=email,
                requester_ip=requester_ip,
                user_agent=user_agent,
                metadata={"retryAfterSeconds": retry_after_seconds},
            )
            return jsonify(
                {
                    "success": False,
                    "message": "Too many reset requests. Please wait and try again.",
                }
            ), 429

        email_svc = EmailService(
            current_app.config["SMTP_HOST"],
            current_app.config["SMTP_PORT"],
            current_app.config["SMTP_USER"],
            current_app.config["SMTP_PASSWORD"],
            current_app.config["SMTP_FROM"],
            current_app.config["SMTP_TLS"],
        )

        # ── set audit TTL on the service instance ─────────────────────────────
        service._audit_ttl_days = int(current_app.config.get("AUDIT_LOG_TTL_DAYS", 90))

        result = service.request_password_reset(
            email=email,
            email_service=email_svc,
            frontend_base_url=frontend_base_url,
            token_expiry_minutes=current_app.config["PASSWORD_RESET_TOKEN_EXP_MINUTES"],
            requester_ip=requester_ip,
            user_agent=user_agent,
            branding={
                "appName": current_app.config["APP_NAME"],
                "logoUrl": current_app.config["APP_LOGO_URL"],
                "supportEmail": current_app.config["SUPPORT_EMAIL"],
            },
        )
        return jsonify(result), 200
    except PyMongoError:
        logger.exception("Forgot password DB error")
        return jsonify({
            "success": True,
            "message": "If this email is registered, a password reset link has been sent.",
        }), 200
    except Exception:
        logger.exception("Forgot password error")
        return jsonify({
            "success": True,
            "message": "If this email is registered, a password reset link has been sent.",
        }), 200


@company_bp.route("/company/reset-password", methods=["POST"])
def reset_password():
    """Reset company password with a one-time token."""
    try:
        payload = request.get_json(silent=True) or {}
        token = payload.get("token") or ""
        password = payload.get("password") or ""
        confirm_password = payload.get("confirmPassword") or ""
        requester_ip = _request_ip()
        user_agent = (request.headers.get("User-Agent") or "").strip()

        service = CompanyService(current_app.mongo_db)
        service._audit_ttl_days = int(current_app.config.get("AUDIT_LOG_TTL_DAYS", 90))

        email_svc = EmailService(
            current_app.config["SMTP_HOST"],
            current_app.config["SMTP_PORT"],
            current_app.config["SMTP_USER"],
            current_app.config["SMTP_PASSWORD"],
            current_app.config["SMTP_FROM"],
            current_app.config["SMTP_TLS"],
        )

        result = service.reset_password(
            token,
            password,
            confirm_password,
            requester_ip=requester_ip,
            user_agent=user_agent,
            email_service=email_svc,
            admin_alert_email=current_app.config.get("ADMIN_ALERT_EMAIL", ""),
            secret_key=current_app.config["SECRET_KEY"],
            password_history_size=int(current_app.config.get("PASSWORD_HISTORY_SIZE", 5)),
            max_failed_resets=int(current_app.config.get("MAX_FAILED_RESETS_BEFORE_LOCK", 10)),
            lock_duration_minutes=int(current_app.config.get("ACCOUNT_LOCK_DURATION_MINUTES", 60)),
        )
        status_code = 200 if result.get("success") else 400
        return jsonify(result), status_code
    except PyMongoError:
        logger.exception("Reset password DB error")
        return jsonify({"success": False, "message": "Database unavailable. Please try again shortly."}), 503
    except Exception:
        logger.exception("Reset password error")
        return jsonify({"success": False, "message": "Could not reset password"}), 500


@company_bp.route("/company/reset-password/validate", methods=["POST"])
def validate_reset_password_token():
    """Validate password reset token before rendering the reset form UX."""
    try:
        payload = request.get_json(silent=True) or {}
        token = payload.get("token") or ""

        service = CompanyService(current_app.mongo_db)
        result = service.validate_reset_token(token)
        status_code = 200 if result.get("success") else 400
        return jsonify(result), status_code
    except PyMongoError:
        logger.exception("Validate reset token DB error")
        return jsonify({"success": False, "message": "Database unavailable. Please try again shortly."}), 503
    except Exception:
        logger.exception("Validate reset token error")
        return jsonify({"success": False, "message": "Could not validate reset link"}), 500


@company_bp.route("/company/<company_id>/email-template", methods=["GET"])
@require_auth
def get_email_template(company_id):
    """Return the company's saved selection notification email template."""
    try:
        service = CompanyService(current_app.mongo_db)
        template = service.get_email_template(company_id)
        if template:
            return jsonify({"success": True, "template": template}), 200
        # Return defaults so the frontend can pre-fill the form
        return jsonify({
            "success": True,
            "template": {
                "subject": "Congratulations! You have been shortlisted for {jobTitle}",
                "body": (
                    "Dear {candidateName},\n\n"
                    "We are pleased to inform you that your application for the position of "
                    "{jobTitle} at {companyName} has been shortlisted by our AI-powered system.\n\n"
                    "Your AI match score: {score}\n\n"
                    "Our hiring team will review your profile and reach out to you with the next steps.\n\n"
                    "For any enquiries, feel free to contact us at: {contactEmail}\n\n"
                    "Best regards,\n"
                    "{companyName} Hiring Team"
                ),
            },
        }), 200
    except Exception:
        logger.exception("Error fetching email template for company %s", company_id)
        return jsonify({"success": False, "message": "Could not fetch template"}), 500


@company_bp.route("/company/<company_id>/email-template", methods=["POST"])
@require_auth
def save_email_template(company_id):
    """Save or update the company's custom selection notification email template."""
    try:
        payload = request.get_json(silent=True) or {}
        subject = (payload.get("subject") or "").strip()
        body = (payload.get("body") or "").strip()

        if not subject or not body:
            return jsonify({"success": False, "message": "Subject and body are required"}), 400

        if len(subject) > 300:
            return jsonify({"success": False, "message": "Subject must be under 300 characters"}), 400

        if len(body) > 5000:
            return jsonify({"success": False, "message": "Body must be under 5000 characters"}), 400

        service = CompanyService(current_app.mongo_db)
        result = service.save_email_template(company_id, subject, body)
        logger.info("Email template saved for company %s", company_id)
        return jsonify(result), 200
    except Exception:
        logger.exception("Error saving email template for company %s", company_id)
        return jsonify({"success": False, "message": "Could not save template"}), 500


@company_bp.route("/company/<company_id>/score-threshold", methods=["GET"])
@require_auth
def get_company_score_threshold(company_id):
    """Get company-specific candidate selection threshold (0-100)."""
    try:
        service = CompanyService(current_app.mongo_db)
        value = service.get_score_threshold(company_id)
        if value is None:
            value = float(current_app.config.get("SCORE_THRESHOLD", 70))
        return jsonify({"success": True, "scoreThreshold": value}), 200
    except Exception:
        logger.exception("Error fetching score threshold for company %s", company_id)
        return jsonify({"success": False, "message": "Could not fetch score threshold"}), 500


@company_bp.route("/company/<company_id>/score-threshold", methods=["POST"])
@require_auth
def save_company_score_threshold(company_id):
    """Save company-specific candidate selection threshold (0-100)."""
    try:
        payload = request.get_json(silent=True) or {}
        raw = payload.get("scoreThreshold", None)
        if raw is None:
            return jsonify({"success": False, "message": "scoreThreshold is required"}), 400

        try:
            value = float(raw)
        except (TypeError, ValueError):
            return jsonify({"success": False, "message": "scoreThreshold must be numeric"}), 400

        if value < 0 or value > 100:
            return jsonify({"success": False, "message": "scoreThreshold must be between 0 and 100"}), 400

        service = CompanyService(current_app.mongo_db)
        result = service.save_score_threshold(company_id, value)
        status = 200 if result.get("success") else 404
        return jsonify(result), status
    except Exception:
        logger.exception("Error saving score threshold for company %s", company_id)
        return jsonify({"success": False, "message": "Could not save score threshold"}), 500
