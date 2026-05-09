"""
models.py - Database schema definitions and automatic setup.

Defines collection names, document field constants, JSON Schema validators,
and a ``setup_database()`` function that creates every collection and all
required indexes at startup.

Safe to call on every startup — MongoDB silently skips collections and
indexes that already exist.
"""

import logging

from pymongo import ASCENDING, DESCENDING
from pymongo.errors import CollectionInvalid

from .utils.ttl_indexes import ensure_indexes

logger = logging.getLogger(__name__)


# ── Collection names ──────────────────────────────────────────────────────────

COLLECTION_COMPANIES = "companies"
COLLECTION_JOBS = "jobs"
COLLECTION_APPLICATIONS = "applications"
COLLECTION_FEEDBACK = "feedback"
COLLECTION_AUDIT_LOGS = "password_reset_audit_logs"
COLLECTION_RATE_LIMITS = "password_reset_rate_limits"
COLLECTION_EMAIL_EVENTS = "email_delivery_events"

ALL_COLLECTIONS = (
    COLLECTION_COMPANIES,
    COLLECTION_JOBS,
    COLLECTION_APPLICATIONS,
    COLLECTION_FEEDBACK,
    COLLECTION_AUDIT_LOGS,
    COLLECTION_RATE_LIMITS,
    COLLECTION_EMAIL_EVENTS,
)


# ── JSON Schema validators ────────────────────────────────────────────────────
# validationAction is set to "warn" so that legacy documents or partial
# updates are never silently rejected — the app stays operational while
# the schema acts as living documentation.

_COMPANIES_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["companyId", "name", "registrationNo", "email", "passwordHash", "createdAt"],
        "properties": {
            "companyId":      {"bsonType": "string", "description": "Unique company identifier (UUID hex)"},
            "name":           {"bsonType": "string", "description": "Company display name"},
            "registrationNo": {"bsonType": "string", "description": "Company registration number"},
            "email":          {"bsonType": "string", "description": "Login email (unique, lowercase)"},
            "passwordHash":   {"bsonType": "string", "description": "bcrypt password hash"},
            "scoreThreshold": {
                "bsonType": ["double", "int"],
                "minimum": 0,
                "maximum": 100,
                "description": "Minimum score to shortlist candidates (0-100)",
            },
            "createdAt": {"bsonType": "string", "description": "ISO 8601 creation timestamp"},
        },
    }
}

_JOBS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["jobId", "title", "description", "companyId", "status", "postDate"],
        "properties": {
            "jobId":              {"bsonType": "string"},
            "title":              {"bsonType": "string"},
            "description":        {"bsonType": "string"},
            "descriptionPdfPath": {"bsonType": ["string", "null"]},
            "companyId":          {"bsonType": "string"},
            "companyName":        {"bsonType": ["string", "null"]},
            "companyRegNo":       {"bsonType": ["string", "null"]},
            "companyEmail":       {"bsonType": ["string", "null"]},
            "location":           {"bsonType": ["string", "null"]},
            "experience":         {"bsonType": ["string", "null"]},
            "status":             {"bsonType": "string", "enum": ["active", "inactive"]},
            "postDate":           {"bsonType": "string"},
            "jd_hash":            {"bsonType": ["string", "null"]},
        },
    }
}

_APPLICATIONS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["applicationId", "jobId", "companyId", "candidateName", "email", "status", "createdAt"],
        "properties": {
            "applicationId": {"bsonType": "string"},
            "jobId":         {"bsonType": "string"},
            "jobTitle":      {"bsonType": ["string", "null"]},
            "companyId":     {"bsonType": "string"},
            "companyRegNo":  {"bsonType": ["string", "null"]},
            "candidateName": {"bsonType": "string"},
            "email":         {"bsonType": "string"},
            "phone":         {"bsonType": ["string", "null"]},
            "degree":        {"bsonType": ["string", "null"]},
            "branch":        {"bsonType": ["string", "null"]},
            "resumeName":    {"bsonType": ["string", "null"]},
            "resumePdfPath": {"bsonType": ["string", "null"]},
            "status": {
                "bsonType": "string",
                "enum": ["processing", "Selected", "Rejected", "error"],
            },
            "score":     {"bsonType": ["double", "int", "null"]},
            "emailSent": {"bsonType": ["bool", "null"]},
            "createdAt": {"bsonType": "string"},
        },
    }
}

_FEEDBACK_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["resume_id", "job_id", "selected", "timestamp"],
        "properties": {
            "resume_id":        {"bsonType": "string"},
            "job_id":           {"bsonType": "string"},
            "semantic_score":   {"bsonType": ["double", "int", "null"]},
            "experience_score": {"bsonType": ["double", "int", "null"]},
            "education_score":  {"bsonType": ["double", "int", "null"]},
            "selected":         {"bsonType": "bool"},
            "timestamp":        {"bsonType": "string"},
            "recruiter_notes":  {"bsonType": ["string", "null"]},
            "user_id":          {"bsonType": ["string", "null"]},
        },
    }
}


# ── Internal helpers ──────────────────────────────────────────────────────────

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


def _create_collection(db, name: str, validator: dict | None = None) -> None:
    """Create a collection with an optional JSON Schema validator.

    If the collection already exists its validator is updated in-place so
    the schema always reflects the latest definition.
    """
    try:
        kwargs: dict = {}
        if validator:
            kwargs["validator"] = validator
            kwargs["validationAction"] = "warn"
        db.create_collection(name, **kwargs)
        logger.info("Created collection: %s", name)
    except CollectionInvalid:
        # Collection already exists — update the validator so it stays current.
        if validator:
            try:
                db.command("collMod", name, validator=validator, validationAction="warn")
                logger.debug("Updated validator for existing collection: %s", name)
            except Exception as exc:
                logger.warning("Could not update validator for %s: %s", name, exc)
    except Exception as exc:
        logger.warning("Could not create collection %s: %s", name, exc)


def _ensure_core_indexes(db) -> None:
    """Create indexes for the core business collections."""

    # ── companies ─────────────────────────────────────────────────────────────
    _safe_create(
        db[COLLECTION_COMPANIES],
        [("email", ASCENDING)],
        name="email_unique",
        unique=True,
        background=True,
    )
    _safe_create(
        db[COLLECTION_COMPANIES],
        [("companyId", ASCENDING)],
        name="company_id_unique",
        unique=True,
        background=True,
    )

    # ── jobs ──────────────────────────────────────────────────────────────────
    _safe_create(
        db[COLLECTION_JOBS],
        [("jobId", ASCENDING)],
        name="job_id_unique",
        unique=True,
        background=True,
    )
    _safe_create(
        db[COLLECTION_JOBS],
        [("companyId", ASCENDING), ("postDate", DESCENDING)],
        name="company_post_date",
        background=True,
    )
    _safe_create(
        db[COLLECTION_JOBS],
        [("status", ASCENDING), ("postDate", DESCENDING)],
        name="status_post_date",
        background=True,
    )
    _safe_create(
        db[COLLECTION_JOBS],
        [("jd_hash", ASCENDING)],
        name="jd_hash",
        sparse=True,
        background=True,
    )

    # ── applications ──────────────────────────────────────────────────────────
    _safe_create(
        db[COLLECTION_APPLICATIONS],
        [("applicationId", ASCENDING)],
        name="application_id_unique",
        unique=True,
        background=True,
    )
    _safe_create(
        db[COLLECTION_APPLICATIONS],
        [("jobId", ASCENDING), ("score", DESCENDING)],
        name="job_score",
        background=True,
    )
    _safe_create(
        db[COLLECTION_APPLICATIONS],
        [("companyId", ASCENDING), ("createdAt", DESCENDING)],
        name="company_created",
        background=True,
    )
    _safe_create(
        db[COLLECTION_APPLICATIONS],
        [("email", ASCENDING), ("jobId", ASCENDING)],
        name="email_job",
        background=True,
    )
    _safe_create(
        db[COLLECTION_APPLICATIONS],
        [("status", ASCENDING)],
        name="status",
        background=True,
    )


# ── Public API ────────────────────────────────────────────────────────────────

def setup_database(db, *, audit_ttl_days: int = 90, rate_limit_ttl_days: int = 7) -> None:
    """Create all collections with schema validation and ensure every index.

    Call this once at application startup (after ``init_mongo``).  MongoDB
    silently skips collections and indexes that already exist, so this is
    always safe to call — even on a populated production database.

    Args:
        db: PyMongo database instance (``app.mongo_db``).
        audit_ttl_days: Retention period in days for password-reset audit logs.
        rate_limit_ttl_days: Retention period in days for rate-limit records.
    """
    # 1. Create / validate collections
    _create_collection(db, COLLECTION_COMPANIES, _COMPANIES_VALIDATOR)
    _create_collection(db, COLLECTION_JOBS, _JOBS_VALIDATOR)
    _create_collection(db, COLLECTION_APPLICATIONS, _APPLICATIONS_VALIDATOR)
    _create_collection(db, COLLECTION_FEEDBACK, _FEEDBACK_VALIDATOR)
    _create_collection(db, COLLECTION_AUDIT_LOGS)
    _create_collection(db, COLLECTION_RATE_LIMITS)
    _create_collection(db, COLLECTION_EMAIL_EVENTS)

    # 2. Core business indexes (companies, jobs, applications)
    _ensure_core_indexes(db)

    # 3. Operational indexes (feedback TTL, audit-log TTL, rate limits, email events)
    ensure_indexes(db, audit_ttl_days=audit_ttl_days, rate_limit_ttl_days=rate_limit_ttl_days)

    logger.info("Database setup complete — all collections and indexes are ready.")
