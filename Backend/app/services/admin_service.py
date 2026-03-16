"""
Admin service — queries and exports for audit logs, system metrics, and cleanup.

All methods accept a PyMongo database object and return plain dicts or lists.
"""

import csv
import io
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


class AdminService:

    def __init__(self, db) -> None:
        self._db = db
        self._audit = db["password_reset_audit_logs"]
        self._rate  = db["password_reset_rate_limits"]
        self._events = db["email_delivery_events"]
        self._companies = db["companies"]
        self._apps = db["applications"]

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc)

    # ── audit log search ──────────────────────────────────────────────────────

    def query_audit_logs(
        self,
        *,
        date_from: str | None = None,
        date_to: str | None = None,
        ip_address: str | None = None,
        email_masked: str | None = None,
        outcome: str | None = None,
        event: str | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> dict:
        """
        Search audit logs with optional filters.

        Returns ``{"logs": [...], "total": int, "page": int, "limit": int}``.
        """
        filt: dict = {}

        if date_from or date_to:
            date_filt: dict = {}
            if date_from:
                date_filt["$gte"] = date_from.strip()
            if date_to:
                date_filt["$lte"] = date_to.strip()
            filt["createdAt"] = date_filt

        if ip_address:
            filt["ipAddress"] = {"$regex": ip_address.strip(), "$options": "i"}

        if email_masked:
            filt["emailMasked"] = {"$regex": email_masked.strip(), "$options": "i"}

        if outcome:
            filt["outcome"] = outcome.strip()

        if event:
            filt["event"] = event.strip()

        page  = max(1, page)
        limit = min(max(1, limit), 200)
        skip  = (page - 1) * limit

        try:
            total = self._audit.count_documents(filt)
            cursor = (
                self._audit.find(filt, {"_id": 0, "_expires": 0})
                .sort("createdAt", -1)
                .skip(skip)
                .limit(limit)
            )
            logs = list(cursor)
        except Exception:
            logger.exception("Audit log query failed")
            return {"logs": [], "total": 0, "page": page, "limit": limit}

        return {"logs": logs, "total": total, "page": page, "limit": limit}

    # ── CSV export ────────────────────────────────────────────────────────────

    def export_audit_logs_csv(
        self,
        *,
        date_from: str | None = None,
        date_to: str | None = None,
        ip_address: str | None = None,
        email_masked: str | None = None,
        outcome: str | None = None,
        event: str | None = None,
        max_rows: int = 10_000,
    ) -> str:
        """Return audit logs as a UTF-8 CSV string (max ``max_rows`` rows)."""
        filt: dict = {}
        if date_from or date_to:
            date_filt: dict = {}
            if date_from:
                date_filt["$gte"] = date_from.strip()
            if date_to:
                date_filt["$lte"] = date_to.strip()
            filt["createdAt"] = date_filt
        if ip_address:
            filt["ipAddress"] = {"$regex": ip_address.strip(), "$options": "i"}
        if email_masked:
            filt["emailMasked"] = {"$regex": email_masked.strip(), "$options": "i"}
        if outcome:
            filt["outcome"] = outcome.strip()
        if event:
            filt["event"] = event.strip()

        fields = [
            "createdAt", "event", "outcome", "emailMasked", "companyId",
            "ipAddress", "userAgent", "requestTime", "resetTime",
        ]

        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()

        try:
            cursor = (
                self._audit.find(filt, {"_id": 0, "_expires": 0})
                .sort("createdAt", -1)
                .limit(max_rows)
            )
            for doc in cursor:
                writer.writerow({f: doc.get(f, "") for f in fields})
        except Exception:
            logger.exception("Audit log CSV export failed")

        return buf.getvalue()

    # ── metrics ───────────────────────────────────────────────────────────────

    def get_metrics(self) -> dict:
        """Return a snapshot of key operational metrics."""
        now = self._utc_now()
        day_ago = (now - timedelta(hours=24)).isoformat()
        week_ago = (now - timedelta(days=7)).isoformat()

        try:
            total_companies   = self._companies.count_documents({})
            total_applications = self._apps.count_documents({})
            selected_count    = self._apps.count_documents({"status": "Selected"})
            rejected_count    = self._apps.count_documents({"status": "Rejected"})
            processing_count  = self._apps.count_documents({"status": "processing"})

            audits_24h = self._audit.count_documents({"createdAt": {"$gte": day_ago}})
            audits_7d  = self._audit.count_documents({"createdAt": {"$gte": week_ago}})
            rate_limit_hits_24h = self._audit.count_documents({
                "outcome": "rate-limited",
                "createdAt": {"$gte": day_ago},
            })
            failed_resets_24h = self._audit.count_documents({
                "event": "password_reset_completed",
                "outcome": {"$ne": "success"},
                "createdAt": {"$gte": day_ago},
            })
            successful_resets_24h = self._audit.count_documents({
                "event": "password_reset_completed",
                "outcome": "success",
                "createdAt": {"$gte": day_ago},
            })
            email_events_total = self._events.count_documents({})

            active_rate_limits = self._rate.count_documents(
                {"windowEndsAt": {"$gt": now.isoformat()}}
            )

        except Exception:
            logger.exception("Metrics collection failed")
            return {"error": "Metrics temporarily unavailable"}

        return {
            "generatedAt": now.isoformat(),
            "companies": {
                "total": total_companies,
            },
            "applications": {
                "total": total_applications,
                "selected": selected_count,
                "rejected": rejected_count,
                "processing": processing_count,
            },
            "security": {
                "auditLogs24h": audits_24h,
                "auditLogs7d": audits_7d,
                "rateLimitHits24h": rate_limit_hits_24h,
                "failedPasswordResets24h": failed_resets_24h,
                "successfulPasswordResets24h": successful_resets_24h,
                "activeRateLimitBuckets": active_rate_limits,
            },
            "email": {
                "deliveryEventsTracked": email_events_total,
            },
        }

    # ── cleanup ───────────────────────────────────────────────────────────────

    def cleanup_old_records(
        self,
        *,
        audit_ttl_days: int = 90,
        rate_limit_ttl_days: int = 7,
    ) -> dict:
        """
        Delete old records not covered by TTL indexes (e.g. legacy docs without
        the ``_expires`` field).

        Returns counts of deleted documents.
        """
        now = self._utc_now()
        audit_cutoff = (now - timedelta(days=audit_ttl_days)).isoformat()
        rate_cutoff  = now.isoformat()       # delete any bucket whose window has closed

        deleted_audit = 0
        deleted_rate  = 0
        deleted_events = 0

        try:
            res = self._audit.delete_many({"createdAt": {"$lt": audit_cutoff}})
            deleted_audit = res.deleted_count
        except Exception:
            logger.exception("Audit log cleanup failed")

        try:
            res = self._rate.delete_many({"windowEndsAt": {"$lt": rate_cutoff}})
            deleted_rate = res.deleted_count
        except Exception:
            logger.exception("Rate-limit record cleanup failed")

        try:
            event_cutoff = (now - timedelta(days=audit_ttl_days)).isoformat()
            res = self._events.delete_many({"timestamp": {"$lt": event_cutoff}})
            deleted_events = res.deleted_count
        except Exception:
            logger.exception("Email events cleanup failed")

        logger.info(
            "Cleanup complete: %d audit logs, %d rate-limit buckets, %d email events deleted",
            deleted_audit, deleted_rate, deleted_events,
        )
        return {
            "deletedAuditLogs": deleted_audit,
            "deletedRateLimitRecords": deleted_rate,
            "deletedEmailEvents": deleted_events,
        }
