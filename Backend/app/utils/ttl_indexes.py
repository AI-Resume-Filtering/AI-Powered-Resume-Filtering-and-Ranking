"""
Create and ensure TTL + query indexes on operational MongoDB collections.

Safe to call at every startup — MongoDB skips creation if the index already exists.
New audit-log documents carry a ``_expires`` BSON datetime field so the TTL monitor
can remove them automatically.  Legacy documents (without the field) are ignored by
the TTL monitor and can be purged via the admin /cleanup endpoint.
"""

import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


# ── helpers ──────────────────────────────────────────────────────────────────

def _safe_create(collection, keys, **kwargs) -> None:
    """Create an index without raising if it already exists or fails."""
    try:
        collection.create_index(keys, **kwargs)
    except Exception as exc:
        logger.warning(
            "Could not create index on %s (%s): %s",
            collection.name,
            kwargs.get("name", ""),
            exc,
        )


# ── public API ────────────────────────────────────────────────────────────────

def ensure_indexes(db, *, audit_ttl_days: int = 90, rate_limit_ttl_days: int = 7) -> None:
    """Idempotently create all required indexes."""

    # ── password_reset_audit_logs ─────────────────────────────────────────────
    # TTL: delete documents when `_expires` datetime is reached (expireAfterSeconds=0)
    _safe_create(
        db["password_reset_audit_logs"],
        [("_expires", 1)],
        name="ttl_expires",
        expireAfterSeconds=0,
        background=True,
    )
    # Query indexes for admin search
    _safe_create(
        db["password_reset_audit_logs"],
        [("ipAddress", 1), ("createdAt", -1)],
        name="ip_created",
        background=True,
    )
    _safe_create(
        db["password_reset_audit_logs"],
        [("emailHash", 1), ("createdAt", -1)],
        name="email_hash_created",
        background=True,
    )
    _safe_create(
        db["password_reset_audit_logs"],
        [("event", 1), ("outcome", 1), ("createdAt", -1)],
        name="event_outcome_created",
        background=True,
    )
    _safe_create(
        db["password_reset_audit_logs"],
        [("createdAt", -1)],
        name="created_desc",
        background=True,
    )

    # ── password_reset_rate_limits ────────────────────────────────────────────
    # Index on windowEndsAt for cleanup queries
    _safe_create(
        db["password_reset_rate_limits"],
        [("windowEndsAt", 1)],
        name="window_ends",
        background=True,
    )

    # ── email_delivery_events (webhook payloads) ──────────────────────────────
    _safe_create(
        db["email_delivery_events"],
        [("messageId", 1)],
        name="message_id",
        unique=True,
        sparse=True,
        background=True,
    )
    _safe_create(
        db["email_delivery_events"],
        [("_expires", 1)],
        name="ttl_expires",
        expireAfterSeconds=0,
        background=True,
    )
    _safe_create(
        db["email_delivery_events"],
        [("event", 1), ("timestamp", -1)],
        name="event_ts",
        background=True,
    )

    # ── feedback (self-learning system) ───────────────────────────────────────
    # Core query indexes for fast feedback retrieval
    _safe_create(
        db["feedback"],
        [("resume_id", 1), ("job_id", 1)],
        name="resume_job_composite",
        background=True,
    )
    _safe_create(
        db["feedback"],
        [("job_id", 1), ("timestamp", -1)],
        name="job_timestamp",
        background=True,
    )
    _safe_create(
        db["feedback"],
        [("resume_id", 1), ("timestamp", -1)],
        name="resume_timestamp",
        background=True,
    )
    _safe_create(
        db["feedback"],
        [("selected", 1), ("timestamp", -1)],
        name="selected_timestamp",
        background=True,
    )
    # TTL index: auto-delete feedback older than 1 year for GDPR compliance
    _safe_create(
        db["feedback"],
        [("timestamp", 1)],
        name="ttl_timestamp",
        expireAfterSeconds=31536000,  # 365 days in seconds
        background=True,
    )

    logger.info(
        "Database indexes ensured (audit TTL=%dd, rate-limit TTL=%dd)",
        audit_ttl_days,
        rate_limit_ttl_days,
    )


def ttl_expires_at(ttl_days: int) -> datetime:
    """Return a UTC datetime ``ttl_days`` from now — store this in ``_expires``."""
    return datetime.now(timezone.utc) + timedelta(days=ttl_days)
