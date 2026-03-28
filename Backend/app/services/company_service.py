import uuid
import hashlib
import secrets
import logging
import re
from html import escape
from datetime import datetime, timedelta, timezone

from .auth_service import hash_password, verify_password, generate_token


logger = logging.getLogger(__name__)
DEFAULT_COMPANY_SCORE_THRESHOLD = 70.0


class CompanyService:
    def __init__(self, db):
        self.collection = db["companies"]
        self.reset_audit_collection = db["password_reset_audit_logs"]
        self._audit_ttl_days: int = 90  # overridden by app config at call sites

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _parse_iso_datetime(value: str) -> datetime | None:
        if not value:
            return None
        try:
            parsed = datetime.fromisoformat(value)
            # Keep comparisons consistent for legacy timestamps missing timezone info.
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _company_selector(company: dict) -> dict:
        """Choose a stable selector across new and legacy company records."""
        company_id = company.get("companyId")
        if company_id:
            return {"companyId": company_id}

        mongo_id = company.get("_id")
        if mongo_id is not None:
            return {"_id": mongo_id}

        email = (company.get("email") or "").strip().lower()
        if email:
            return {"email": email}

        return {}

    @staticmethod
    def _mask_email(email: str) -> str:
        normalized = (email or "").strip().lower()
        if "@" not in normalized:
            return ""
        local_part, domain = normalized.split("@", 1)
        if len(local_part) <= 2:
            masked_local = local_part[:1] + "*"
        else:
            masked_local = local_part[:2] + ("*" * (len(local_part) - 2))
        return f"{masked_local}@{domain}"

    @staticmethod
    def _email_fingerprint(email: str) -> str:
        normalized = (email or "").strip().lower()
        if not normalized:
            return ""
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @staticmethod
    def _safe_user_agent(user_agent: str) -> str:
        ua = (user_agent or "").strip()
        return ua[:255]

    def _log_password_reset_audit(
        self,
        *,
        event: str,
        outcome: str,
        email: str = "",
        company: dict | None = None,
        requester_ip: str = "",
        user_agent: str = "",
        request_time: datetime | None = None,
        reset_time: datetime | None = None,
        metadata: dict | None = None,
    ) -> None:
        doc = {
            "event": event,
            "outcome": outcome,
            "emailHash": self._email_fingerprint(email),
            "emailMasked": self._mask_email(email),
            "companyId": (company or {}).get("companyId"),
            "requestTime": request_time.isoformat() if request_time else None,
            "resetTime": reset_time.isoformat() if reset_time else None,
            "ipAddress": (requester_ip or "").strip(),
            "userAgent": self._safe_user_agent(user_agent),
            "metadata": metadata or {},
            "createdAt": self._utc_now().isoformat(),
        }
        doc["_expires"] = self._ttl_expires()
        try:
            self.reset_audit_collection.insert_one(doc)
        except Exception:
            logger.warning("Failed to persist password reset audit log", exc_info=True)

    def _ttl_expires(self) -> datetime:
        """Return the BSON datetime at which a new audit-log doc should expire."""
        return self._utc_now() + timedelta(days=max(1, self._audit_ttl_days))

    def log_password_reset_audit(self, **kwargs) -> None:
        self._log_password_reset_audit(**kwargs)

    @staticmethod
    def _build_reset_email_html(
        company_name: str,
        reset_link: str,
        valid_minutes: int,
        branding: dict,
    ) -> str:
        safe_company_name = escape(company_name or "Team")
        safe_link = escape(reset_link)
        safe_app_name = escape((branding or {}).get("appName") or "Resume Filtering Platform")
        safe_support_email = escape((branding or {}).get("supportEmail") or "")
        logo_url = ((branding or {}).get("logoUrl") or "").strip()
        safe_logo_url = escape(logo_url)
        has_logo = bool(logo_url)

        logo_html = (
            f'<img src="{safe_logo_url}" alt="{safe_app_name} logo" '
            'style="max-height:56px;max-width:180px;display:block;margin:0 auto 18px auto;" />'
            if has_logo
            else (
                '<div style="width:56px;height:56px;border-radius:12px;background:#0b3d91;color:#ffffff;'
                'font-weight:700;line-height:56px;text-align:center;margin:0 auto 18px auto;">RF</div>'
            )
        )

        support_html = (
            f'<p style="margin:20px 0 0 0;color:#4b5563;font-size:13px;">Need help? '
            f'Contact us at <a href="mailto:{safe_support_email}" style="color:#0b3d91;">{safe_support_email}</a>.</p>'
            if safe_support_email
            else ""
        )

        return f"""
<!doctype html>
<html>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:Arial,sans-serif;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="padding:24px 12px;">
        <tr>
            <td align="center">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:620px;background:#ffffff;border-radius:14px;padding:28px;box-shadow:0 8px 20px rgba(0,0,0,0.08);">
                    <tr>
                        <td>
                            {logo_html}
                            <h2 style="margin:0 0 8px 0;color:#111827;font-size:24px;">Reset your password</h2>
                            <p style="margin:0 0 16px 0;color:#374151;line-height:1.6;">Hello {safe_company_name},</p>
                            <p style="margin:0 0 16px 0;color:#374151;line-height:1.6;">We received a request to reset your password for your {safe_app_name} account.</p>
                            <p style="margin:0 0 18px 0;color:#374151;line-height:1.6;">This secure link will expire in <strong>{valid_minutes} minutes</strong>.</p>
                            <p style="margin:0 0 24px 0;">
                                <a href="{safe_link}" style="display:inline-block;padding:12px 22px;background:#0b3d91;color:#ffffff;text-decoration:none;border-radius:8px;font-weight:600;">Reset Password</a>
                            </p>
                            <p style="margin:0 0 8px 0;color:#6b7280;font-size:13px;line-height:1.5;">If the button does not work, copy and paste this URL into your browser:</p>
                            <p style="margin:0 0 10px 0;color:#0b3d91;font-size:13px;word-break:break-all;">{safe_link}</p>
                            <p style="margin:14px 0 0 0;color:#6b7280;font-size:13px;line-height:1.5;">If you did not request this reset, you can safely ignore this email.</p>
                            {support_html}
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
""".strip()

    def register_company(
        self,
        company_name: str,
        registration_no: str,
        email: str,
        password: str,
        score_threshold: float = DEFAULT_COMPANY_SCORE_THRESHOLD,
    ) -> dict:
        email = (email or "").strip().lower()
        existing = self.collection.find_one({"email": email})
        if existing:
            return {"success": False, "message": "Company already exists"}

        company_id = uuid.uuid4().hex
        company = {
            "companyId": company_id,
            "name": company_name,
            "registrationNo": registration_no,
            "email": email,
            "passwordHash": hash_password(password),
            "scoreThreshold": float(score_threshold),
            "createdAt": datetime.utcnow().isoformat(),
        }

        self.collection.insert_one(company)
        return {"success": True, "company": self._public_company(company)}

    def get_score_threshold(self, company_id: str) -> float | None:
        company = self.collection.find_one(
            {"companyId": company_id}, {"scoreThreshold": 1, "_id": 0}
        )
        if not company:
            return None
        try:
            raw = company.get("scoreThreshold", None)
            if raw is None:
                return None
            value = float(raw)
            return max(0.0, min(100.0, value))
        except (TypeError, ValueError):
            return None

    def save_score_threshold(self, company_id: str, threshold: float) -> dict:
        value = max(0.0, min(100.0, float(threshold)))
        result = self.collection.update_one(
            {"companyId": company_id},
            {"$set": {"scoreThreshold": value}},
        )
        if result.matched_count == 0:
            return {"success": False, "message": "Company not found"}
        return {"success": True, "message": "Score threshold saved", "scoreThreshold": value}

    def login_company(self, email: str, password: str) -> dict:
        email = (email or "").strip().lower()
        company = self.collection.find_one({"email": email})
        if not company:
            return {"success": False, "message": "Invalid email or password"}

        if not verify_password(password, company.get("passwordHash", "")):
            return {"success": False, "message": "Invalid email or password"}

        return {"success": True, "company": self._public_company(company)}

    def request_password_reset(
        self,
        email: str,
        email_service,
        frontend_base_url: str,
        token_expiry_minutes: int = 30,
        requester_ip: str = "",
        user_agent: str = "",
        branding: dict | None = None,
    ) -> dict:
        """Create a reset token and email it if the company account exists.

        Always return a generic success response to prevent account enumeration.
        """
        generic_response = {
            "success": True,
            "message": "If this email is registered, a password reset link has been sent.",
        }

        normalized_email = (email or "").strip().lower()
        if not normalized_email:
            self._log_password_reset_audit(
                event="password_reset_requested",
                outcome="invalid-email",
                email=email,
                requester_ip=requester_ip,
                user_agent=user_agent,
            )
            return generic_response

        company = self.collection.find_one({"email": normalized_email})
        if not company:
            self._log_password_reset_audit(
                event="password_reset_requested",
                outcome="account-not-found",
                email=normalized_email,
                requester_ip=requester_ip,
                user_agent=user_agent,
            )
            return generic_response

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        requested_at = self._utc_now()
        expires_at = requested_at + timedelta(minutes=max(5, token_expiry_minutes))
        selector = self._company_selector(company)
        if not selector:
            logger.warning("Could not determine selector for password reset request: %s", normalized_email)
            self._log_password_reset_audit(
                event="password_reset_requested",
                outcome="selector-resolution-failed",
                email=normalized_email,
                company=company,
                requester_ip=requester_ip,
                user_agent=user_agent,
            )
            return generic_response

        update_result = self.collection.update_one(
            selector,
            {
                "$set": {
                    "passwordReset": {
                        "tokenHash": token_hash,
                        "expiresAt": expires_at.isoformat(),
                        "requestedAt": requested_at.isoformat(),
                        "requestedIp": (requester_ip or "").strip(),
                        "requestedUserAgent": self._safe_user_agent(user_agent),
                    }
                }
            },
        )
        if update_result.matched_count == 0:
            logger.warning("Password reset token update did not match any record for email: %s", normalized_email)
            self._log_password_reset_audit(
                event="password_reset_requested",
                outcome="token-persist-failed",
                email=normalized_email,
                company=company,
                requester_ip=requester_ip,
                user_agent=user_agent,
            )
            return generic_response

        base_url = (frontend_base_url or "http://localhost:5173").rstrip("/")
        reset_link = f"{base_url}/reset-password?token={raw_token}"
        company_name = company.get("name") or "Team"
        valid_minutes = max(5, token_expiry_minutes)
        app_name = (branding or {}).get("appName") or "Resume Filtering Platform"

        subject = f"Reset your {app_name} account password"
        body = (
            f"Hello {company_name},\n\n"
            "We received a request to reset your account password.\n\n"
            f"Reset link (valid for {valid_minutes} minutes):\n"
            f"{reset_link}\n\n"
            "If you did not request this, you can safely ignore this email.\n\n"
            "Regards,\n"
            f"{app_name}"
        )
        html_body = self._build_reset_email_html(company_name, reset_link, valid_minutes, branding or {})

        sent = email_service.send_email(normalized_email, subject, body, html_body=html_body)

        if sent:
            self.collection.update_one(
                selector,
                {"$set": {"passwordReset.emailSent": True, "passwordReset.emailSentAt": self._utc_now().isoformat()}},
            )
        else:
            self.collection.update_one(
                selector,
                {"$set": {"passwordReset.emailSent": False}, "$unset": {"passwordReset.emailSentAt": ""}},
            )

        self._log_password_reset_audit(
            event="password_reset_requested",
            outcome="email-sent" if sent else "email-send-failed",
            email=normalized_email,
            company=company,
            requester_ip=requester_ip,
            user_agent=user_agent,
            request_time=requested_at,
            metadata={"expiresAt": expires_at.isoformat(), "frontendBaseUrl": base_url},
        )
        return generic_response

    def validate_reset_token(self, token: str) -> dict:
        """Validate reset token and return whether it can still be used."""
        token = (token or "").strip()
        if not token:
            return {"success": False, "message": "Reset token is required"}

        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        company = self.collection.find_one({"passwordReset.tokenHash": token_hash})
        if not company:
            return {"success": False, "message": "Reset link is invalid or expired"}

        selector = self._company_selector(company)
        if not selector:
            return {"success": False, "message": "Reset link is invalid or expired"}

        reset_info = company.get("passwordReset") or {}
        expires_at = self._parse_iso_datetime(reset_info.get("expiresAt", ""))
        if not expires_at or self._utc_now() > expires_at:
            self.collection.update_one(selector, {"$unset": {"passwordReset": ""}})
            return {"success": False, "message": "Reset link is invalid or expired"}

        return {"success": True, "message": "Reset link is valid"}

    @staticmethod
    def _validate_password_strength(password: str) -> str | None:
        """Return validation error message when password does not meet policy."""
        if len(password) < 8:
            return "Password must be at least 8 characters"
        if len(password) > 128:
            return "Password is too long (max 128 characters)"
        if not re.search(r"[A-Z]", password):
            return "Password must include at least one uppercase letter"
        if not re.search(r"[a-z]", password):
            return "Password must include at least one lowercase letter"
        if not re.search(r"\d", password):
            return "Password must include at least one number"
        if not re.search(r"[^A-Za-z0-9]", password):
            return "Password must include at least one special character"
        return None

    def reset_password(
        self,
        token: str,
        new_password: str,
        confirm_password: str,
        requester_ip: str = "",
        user_agent: str = "",
        email_service=None,
        admin_alert_email: str = "",
        secret_key: str = "",
        password_history_size: int = 5,
        max_failed_resets: int = 10,
        lock_duration_minutes: int = 60,
    ) -> dict:
        token = (token or "").strip()
        if not token:
            self._log_password_reset_audit(
                event="password_reset_completed",
                outcome="missing-token",
                requester_ip=requester_ip,
                user_agent=user_agent,
            )
            return {"success": False, "message": "Reset token is required"}

        if not new_password or not confirm_password:
            self._log_password_reset_audit(
                event="password_reset_completed",
                outcome="missing-password-fields",
                requester_ip=requester_ip,
                user_agent=user_agent,
            )
            return {"success": False, "message": "Password and confirmation are required"}

        password_policy_error = self._validate_password_strength(new_password)
        if password_policy_error:
            self._log_password_reset_audit(
                event="password_reset_completed",
                outcome="password-policy-failed",
                requester_ip=requester_ip,
                user_agent=user_agent,
                metadata={"reason": password_policy_error},
            )
            return {"success": False, "message": password_policy_error}

        if new_password != confirm_password:
            self._log_password_reset_audit(
                event="password_reset_completed",
                outcome="password-mismatch",
                requester_ip=requester_ip,
                user_agent=user_agent,
            )
            return {"success": False, "message": "Passwords do not match"}

        token_validation = self.validate_reset_token(token)
        if not token_validation.get("success"):
            self._log_password_reset_audit(
                event="password_reset_completed",
                outcome="token-invalid-or-expired",
                requester_ip=requester_ip,
                user_agent=user_agent,
            )
            return token_validation

        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        company = self.collection.find_one({"passwordReset.tokenHash": token_hash})
        if not company:
            self._log_password_reset_audit(
                event="password_reset_completed",
                outcome="token-not-found",
                requester_ip=requester_ip,
                user_agent=user_agent,
            )
            return {"success": False, "message": "Reset link is invalid or expired"}

        selector = self._company_selector(company)
        if not selector:
            self._log_password_reset_audit(
                event="password_reset_completed",
                outcome="selector-resolution-failed",
                email=company.get("email", ""),
                company=company,
                requester_ip=requester_ip,
                user_agent=user_agent,
            )
            return {"success": False, "message": "Reset link is invalid or expired"}

        # ── account lock check ────────────────────────────────────────────────
        is_locked, retry_after = self._is_account_locked(company)
        if is_locked:
            self._log_password_reset_audit(
                event="password_reset_completed",
                outcome="account-locked",
                email=company.get("email", ""),
                company=company,
                requester_ip=requester_ip,
                user_agent=user_agent,
                metadata={"retryAfterSeconds": retry_after},
            )
            return {
                "success": False,
                "message": f"Account temporarily locked. Please try again in {retry_after // 60 + 1} minutes.",
            }

        # ── password history check ────────────────────────────────────────────
        if password_history_size > 0 and self._is_password_reused(company, new_password, password_history_size):
            self._increment_failed_reset_attempts(
                selector, company,
                max_failures=max_failed_resets,
                lock_duration_minutes=lock_duration_minutes,
                email_service=email_service,
                admin_alert_email=admin_alert_email,
            )
            self._log_password_reset_audit(
                event="password_reset_completed",
                outcome="password-reused",
                email=company.get("email", ""),
                company=company,
                requester_ip=requester_ip,
                user_agent=user_agent,
            )
            return {
                "success": False,
                "message": f"You cannot reuse one of your last {password_history_size} passwords.",
            }

        reset_info = company.get("passwordReset") or {}
        request_time = self._parse_iso_datetime(reset_info.get("requestedAt", ""))
        reset_time = self._utc_now()

        new_hash = hash_password(new_password)
        self.collection.update_one(
            selector,
            {
                "$set": {
                    "passwordHash": new_hash,
                    "passwordUpdatedAt": reset_time.isoformat(),
                },
                "$unset": {"passwordReset": ""},
            },
        )

        # ── post-reset housekeeping ───────────────────────────────────────────
        self._record_password_history(selector, new_hash, password_history_size)
        self._clear_failed_reset_attempts(selector)

        self._log_password_reset_audit(
            event="password_reset_completed",
            outcome="success",
            email=company.get("email", ""),
            company=company,
            requester_ip=requester_ip,
            user_agent=user_agent,
            request_time=request_time,
            reset_time=reset_time,
            metadata={"passwordPolicy": "upper-lower-number-special"},
        )

        # ── auto-login data ───────────────────────────────────────────────────
        public = self._public_company(company)
        token_for_login = self._make_login_token(company, secret_key) if secret_key else None
        result: dict = {"success": True, "message": "Password reset successful", "company": public}
        if token_for_login:
            result["token"] = token_for_login
            result["autoLogin"] = True
        return result

    def save_email_template(self, company_id: str, subject: str, body: str) -> dict:
        """Save or update the company's custom selection notification email template."""
        if not subject.strip() or not body.strip():
            return {"success": False, "message": "Subject and body are required"}
        self.collection.update_one(
            {"companyId": company_id},
            {"$set": {"emailTemplate": {"subject": subject.strip(), "body": body.strip()}}},
        )
        return {"success": True, "message": "Email template saved"}

    def get_email_template(self, company_id: str) -> dict | None:
        """Fetch the saved email template for a company. Returns None if not set."""
        company = self.collection.find_one(
            {"companyId": company_id}, {"emailTemplate": 1, "_id": 0}
        )
        if company and company.get("emailTemplate"):
            return company["emailTemplate"]
        return None

    # ── password history ──────────────────────────────────────────────────────

    def _is_password_reused(self, company: dict, new_password: str, history_size: int) -> bool:
        """Return True if ``new_password`` matches any of the last ``history_size`` hashes."""
        history = company.get("passwordHistory") or []
        recent = history[-history_size:] if history_size > 0 else []
        for entry in recent:
            stored_hash = entry.get("hash") if isinstance(entry, dict) else entry
            if stored_hash and verify_password(new_password, stored_hash):
                return True
        return False

    def _record_password_history(
        self, selector: dict, new_hash: str, history_size: int
    ) -> None:
        """Push the new hash to the company's passwordHistory array (capped to history_size)."""
        try:
            self.collection.update_one(
                selector,
                {"$push": {"passwordHistory": {"$each": [{"hash": new_hash, "setAt": self._utc_now().isoformat()}], "$slice": -max(1, history_size)}}},
            )
        except Exception:
            logger.warning("Failed to record password history", exc_info=True)

    # ── account lock ──────────────────────────────────────────────────────────

    def _is_account_locked(self, company: dict) -> tuple[bool, int]:
        """
        Return (is_locked, retry_after_seconds).
        Checks ``accountLockedUntil`` field on the company document.
        """
        locked_until_str = company.get("accountLockedUntil")
        if not locked_until_str:
            return False, 0
        locked_until = self._parse_iso_datetime(locked_until_str)
        if locked_until and self._utc_now() < locked_until:
            retry_after = max(1, int((locked_until - self._utc_now()).total_seconds()))
            return True, retry_after
        return False, 0

    def _increment_failed_reset_attempts(
        self,
        selector: dict,
        company: dict,
        *,
        max_failures: int,
        lock_duration_minutes: int,
        email_service=None,
        admin_alert_email: str = "",
    ) -> None:
        """
        Increment the suspicious-reset counter.  Lock the account and fire an
        admin alert when ``max_failures`` is reached.
        """
        try:
            current = int(company.get("failedResetAttempts") or 0) + 1
            update: dict = {
                "$set": {"failedResetAttempts": current, "lastFailedResetAt": self._utc_now().isoformat()},
            }
            if current >= max(1, max_failures):
                locked_until = self._utc_now() + timedelta(minutes=max(1, lock_duration_minutes))
                update["$set"]["accountLockedUntil"] = locked_until.isoformat()
                logger.warning(
                    "Account locked due to %d failed reset attempts: companyId=%s",
                    current,
                    company.get("companyId"),
                )
                self._send_admin_alert(
                    event="account_locked",
                    company=company,
                    email_service=email_service,
                    admin_alert_email=admin_alert_email,
                    extra={"failedAttempts": current, "lockedUntil": locked_until.isoformat()},
                )
            self.collection.update_one(selector, update)
        except Exception:
            logger.warning("Failed to increment failed reset attempts", exc_info=True)

    def _clear_failed_reset_attempts(self, selector: dict) -> None:
        """Reset the failure counter on a successful password reset."""
        try:
            self.collection.update_one(
                selector,
                {
                    "$unset": {"failedResetAttempts": "", "lastFailedResetAt": "", "accountLockedUntil": ""},
                },
            )
        except Exception:
            logger.warning("Failed to clear failed reset attempts", exc_info=True)

    # ── admin alert ───────────────────────────────────────────────────────────

    def _send_admin_alert(
        self,
        *,
        event: str,
        company: dict,
        email_service=None,
        admin_alert_email: str = "",
        extra: dict | None = None,
    ) -> None:
        """Send a plain-text alert email to the admin address."""
        if not email_service or not admin_alert_email:
            return
        try:
            company_id = company.get("companyId", "unknown")
            company_email = self._mask_email(company.get("email", ""))
            subject = f"[Security Alert] {event} — company {company_email}"
            body_lines = [
                f"Security event: {event}",
                f"Company ID:     {company_id}",
                f"Company email:  {company_email}",
                f"Time (UTC):     {self._utc_now().isoformat()}",
            ]
            for k, v in (extra or {}).items():
                body_lines.append(f"{k}: {v}")
            email_service.send_email(admin_alert_email, subject, "\n".join(body_lines))
        except Exception:
            logger.warning("Failed to send admin security alert", exc_info=True)

    # ── auto-login token ──────────────────────────────────────────────────────

    def _make_login_token(self, company: dict, secret_key: str) -> str | None:
        """Return a fresh JWT for the company (used for auto-login after reset)."""
        company_id = company.get("companyId")
        if not company_id or not secret_key:
            return None
        try:
            return generate_token(company_id, secret_key)
        except Exception:
            logger.warning("Failed to generate post-reset login token", exc_info=True)
            return None

    @staticmethod
    def _public_company(company: dict) -> dict:
        raw_threshold = company.get("scoreThreshold")
        try:
            threshold = float(raw_threshold) if raw_threshold is not None else DEFAULT_COMPANY_SCORE_THRESHOLD
        except (TypeError, ValueError):
            threshold = DEFAULT_COMPANY_SCORE_THRESHOLD
        threshold = max(0.0, min(100.0, threshold))
        return {
            "companyId": company.get("companyId"),
            "name": company.get("name"),
            "registrationNo": company.get("registrationNo"),
            "email": company.get("email"),
            "scoreThreshold": threshold,
        }
