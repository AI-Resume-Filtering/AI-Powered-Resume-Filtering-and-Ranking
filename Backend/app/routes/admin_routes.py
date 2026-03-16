"""
Admin API routes — audit logs, metrics, cleanup, email-delivery webhooks.

All /api/admin/* endpoints require the ``X-Admin-Key`` header to match the
``ADMIN_API_KEY`` environment variable.  If ADMIN_API_KEY is empty the admin
endpoints return 503 so they cannot be used accidentally in an unconfigured
deployment.

Email delivery webhook (``/api/webhooks/email-events``) accepts POST from
mail providers (SendGrid, Mailgun, AWS SES, etc.) and stores events for
visibility.  Protect this route in production with a webhook secret or IP
allowlist via a reverse proxy.
"""

import csv
import io
import logging
from datetime import datetime, timezone
from functools import wraps

from flask import Blueprint, Response, current_app, jsonify, request
from pymongo.errors import PyMongoError

from ..services.admin_service import AdminService

admin_bp = Blueprint("admin", __name__)
logger = logging.getLogger(__name__)


# ── auth decorator ────────────────────────────────────────────────────────────

def require_admin(f):
    """Verify the X-Admin-Key header against ADMIN_API_KEY config."""
    @wraps(f)
    def decorated(*args, **kwargs):
        configured_key = (current_app.config.get("ADMIN_API_KEY") or "").strip()
        if not configured_key:
            return jsonify({
                "success": False,
                "message": "Admin API is not configured. Set ADMIN_API_KEY in your environment.",
            }), 503

        provided_key = (request.headers.get("X-Admin-Key") or "").strip()
        if not provided_key or provided_key != configured_key:
            logger.warning(
                "Admin access denied — bad key from %s",
                (request.headers.get("X-Forwarded-For") or request.remote_addr or ""),
            )
            return jsonify({"success": False, "message": "Forbidden"}), 403
        return f(*args, **kwargs)
    return decorated


# ── helpers ───────────────────────────────────────────────────────────────────

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_int(value, default: int, min_val: int = 1, max_val: int = 200) -> int:
    try:
        return max(min_val, min(int(value), max_val))
    except (TypeError, ValueError):
        return default


# ── audit log endpoints ───────────────────────────────────────────────────────

@admin_bp.route("/admin/audit-logs", methods=["GET"])
@require_admin
def list_audit_logs():
    """
    Search audit logs.

    Query params:
      dateFrom, dateTo  — ISO date strings (YYYY-MM-DD or full ISO-8601)
      ip                — partial IP match
      email             — partial masked email match
      outcome           — exact outcome value
      event             — exact event value
      page, limit       — pagination (limit max 200)
    """
    try:
        svc = AdminService(current_app.mongo_db)
        result = svc.query_audit_logs(
            date_from   = request.args.get("dateFrom") or None,
            date_to     = request.args.get("dateTo") or None,
            ip_address  = request.args.get("ip") or None,
            email_masked= request.args.get("email") or None,
            outcome     = request.args.get("outcome") or None,
            event       = request.args.get("event") or None,
            page        = _parse_int(request.args.get("page"), 1, min_val=1, max_val=10_000),
            limit       = _parse_int(request.args.get("limit"), 50, min_val=1, max_val=200),
        )
        return jsonify({"success": True, **result}), 200
    except PyMongoError:
        logger.exception("Audit log DB error")
        return jsonify({"success": False, "message": "Database unavailable"}), 503
    except Exception:
        logger.exception("Audit log query error")
        return jsonify({"success": False, "message": "Could not retrieve audit logs"}), 500


@admin_bp.route("/admin/audit-logs/export", methods=["GET"])
@require_admin
def export_audit_logs():
    """Export audit logs as a CSV file download (same filters as list endpoint)."""
    try:
        svc = AdminService(current_app.mongo_db)
        csv_data = svc.export_audit_logs_csv(
            date_from   = request.args.get("dateFrom") or None,
            date_to     = request.args.get("dateTo") or None,
            ip_address  = request.args.get("ip") or None,
            email_masked= request.args.get("email") or None,
            outcome     = request.args.get("outcome") or None,
            event       = request.args.get("event") or None,
        )
        filename = f"audit_logs_{_utc_now().strftime('%Y%m%d_%H%M%S')}.csv"
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except PyMongoError:
        logger.exception("Audit export DB error")
        return jsonify({"success": False, "message": "Database unavailable"}), 503
    except Exception:
        logger.exception("Audit export error")
        return jsonify({"success": False, "message": "Could not export audit logs"}), 500


# ── metrics endpoint ─────────────────────────────────────────────────────────

@admin_bp.route("/admin/metrics", methods=["GET"])
@require_admin
def get_metrics():
    """Return a snapshot of key system metrics."""
    try:
        svc = AdminService(current_app.mongo_db)
        metrics = svc.get_metrics()
        return jsonify({"success": True, "metrics": metrics}), 200
    except PyMongoError:
        logger.exception("Metrics DB error")
        return jsonify({"success": False, "message": "Database unavailable"}), 503
    except Exception:
        logger.exception("Metrics error")
        return jsonify({"success": False, "message": "Could not retrieve metrics"}), 500


# ── cleanup endpoint ──────────────────────────────────────────────────────────

@admin_bp.route("/admin/cleanup", methods=["POST"])
@require_admin
def cleanup_records():
    """
    Manually delete old audit logs and expired rate-limit buckets.
    Useful when TTL indexes are not yet set up or for on-demand pruning.
    """
    try:
        svc = AdminService(current_app.mongo_db)
        result = svc.cleanup_old_records(
            audit_ttl_days      = int(current_app.config.get("AUDIT_LOG_TTL_DAYS", 90)),
            rate_limit_ttl_days = int(current_app.config.get("RATE_LIMIT_TTL_DAYS", 7)),
        )
        return jsonify({"success": True, "deleted": result}), 200
    except PyMongoError:
        logger.exception("Cleanup DB error")
        return jsonify({"success": False, "message": "Database unavailable"}), 503
    except Exception:
        logger.exception("Cleanup error")
        return jsonify({"success": False, "message": "Cleanup operation failed"}), 500


# ── email-delivery webhook ────────────────────────────────────────────────────

@admin_bp.route("/webhooks/email-events", methods=["POST"])
def email_delivery_webhook():
    """
    Ingest email delivery events from providers (SendGrid, Mailgun, SES, etc.).

    Expects either a JSON object or a JSON array of event objects.
    Each event is stored in the ``email_delivery_events`` collection for
    visibility (bounces, opens, spam reports, etc.).

    Protect this endpoint with a webhook secret or IP allowlist in production.
    """
    try:
        payload = request.get_json(silent=True) or []
        if isinstance(payload, dict):
            payload = [payload]

        if not isinstance(payload, list):
            return jsonify({"success": False, "message": "Expected JSON array or object"}), 400

        now = _utc_now()
        ttl_days = int(current_app.config.get("AUDIT_LOG_TTL_DAYS", 90))
        expires_at = now + __import__("datetime").timedelta(days=ttl_days)

        collection = current_app.mongo_db["email_delivery_events"]
        inserted = 0

        for raw_event in payload[:100]:  # cap per request
            if not isinstance(raw_event, dict):
                continue
            doc = {
                "event":      raw_event.get("event") or raw_event.get("type") or "unknown",
                "messageId":  raw_event.get("MessageID") or raw_event.get("messageId") or raw_event.get("sg_message_id"),
                "email":      raw_event.get("email") or raw_event.get("recipient"),
                "timestamp":  raw_event.get("timestamp") or now.isoformat(),
                "reason":     raw_event.get("reason") or raw_event.get("description") or "",
                "provider":   raw_event.get("_provider", "unknown"),
                "raw":        raw_event,
                "receivedAt": now.isoformat(),
                "_expires":   expires_at,
            }
            try:
                collection.insert_one(doc)
                inserted += 1
            except Exception:
                pass  # duplicate messageId or other error — skip silently

        return jsonify({"success": True, "accepted": inserted}), 200

    except Exception:
        logger.exception("Email webhook error")
        return jsonify({"success": False, "message": "Webhook processing error"}), 500
