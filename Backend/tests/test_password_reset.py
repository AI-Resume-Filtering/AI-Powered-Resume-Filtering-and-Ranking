"""
End-to-end tests for the password-reset flow.

Covers:
  - valid token — successful reset + auto-login token returned
  - expired token — rejected
  - invalid token — rejected
  - rate-limited request — 429 returned
  - email send failure — generic success still returned (no enumeration)
  - successful password reset and login after reset

Run with:
    cd Backend
    python -m pytest tests/test_password_reset.py -v

Requirements:
    pip install pytest mongomock
    (mongomock provides an in-memory MongoDB client — no running Mongo needed)
"""

import hashlib
import secrets
import sys
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

# ── make Backend/ importable without installing the package ──────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Try mongomock for a lightweight in-memory Mongo; fall back to real pymongo
# if mongomock is not installed (requires a live MongoDB instance).
try:
    import mongomock  # type: ignore
    def _make_db():
        client = mongomock.MongoClient()
        return client["test_db"]
    USING_MOCK = True
except ImportError:
    import pymongo
    def _make_db():
        client = pymongo.MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
        return client["test_password_reset_db"]
    USING_MOCK = False


from app.services.company_service import CompanyService
from app.services.auth_service import hash_password, verify_token


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def db():
    return _make_db()


@pytest.fixture
def service(db):
    svc = CompanyService(db)
    svc._audit_ttl_days = 7
    return svc


@pytest.fixture
def company(db):
    """Insert a test company and return its document."""
    doc = {
        "companyId": "test-company-001",
        "name": "Test Company",
        "registrationNo": "REG001",
        "email": "test@example.com",
        "passwordHash": hash_password("OldPass@123"),
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    db["companies"].insert_one(doc)
    return doc


def _make_email_service(should_fail: bool = False) -> MagicMock:
    svc = MagicMock()
    svc.send_email.return_value = not should_fail
    return svc


SECRET_KEY = "this-is-a-very-long-test-secret-key-for-jwt-signing"
NEW_PASS = "NewPass@456"
CONFIRM_PASS = "NewPass@456"


# ── helpers ───────────────────────────────────────────────────────────────────

def _plant_valid_token(db, company_id: str) -> str:
    """Insert a fresh password reset token into the company document and return the raw token."""
    raw = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw.encode()).hexdigest()
    exp = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
    db["companies"].update_one(
        {"companyId": company_id},
        {"$set": {
            "passwordReset": {
                "tokenHash": token_hash,
                "expiresAt": exp,
                "requestedAt": datetime.now(timezone.utc).isoformat(),
                "requestedIp": "127.0.0.1",
                "requestedUserAgent": "pytest",
            }
        }},
    )
    return raw


def _plant_expired_token(db, company_id: str) -> str:
    raw = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw.encode()).hexdigest()
    exp = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    db["companies"].update_one(
        {"companyId": company_id},
        {"$set": {
            "passwordReset": {
                "tokenHash": token_hash,
                "expiresAt": exp,
                "requestedAt": datetime.now(timezone.utc).isoformat(),
                "requestedIp": "127.0.0.1",
                "requestedUserAgent": "pytest",
            }
        }},
    )
    return raw


# ── tests ─────────────────────────────────────────────────────────────────────

class TestValidToken:
    def test_reset_succeeds_with_valid_token(self, db, service, company):
        token = _plant_valid_token(db, company["companyId"])
        result = service.reset_password(
            token, NEW_PASS, CONFIRM_PASS,
            secret_key=SECRET_KEY,
            password_history_size=5,
        )
        assert result["success"] is True
        assert "Password reset successful" in result["message"]

    def test_reset_returns_auto_login_token(self, db, service, company):
        token = _plant_valid_token(db, company["companyId"])
        result = service.reset_password(
            token, NEW_PASS, CONFIRM_PASS,
            secret_key=SECRET_KEY,
        )
        assert result.get("autoLogin") is True
        assert "token" in result
        # Verify the JWT is valid and identifies the correct company
        decoded_id = verify_token(result["token"], SECRET_KEY)
        assert decoded_id == company["companyId"]

    def test_reset_clears_failed_attempts_counter(self, db, service, company):
        db["companies"].update_one(
            {"companyId": company["companyId"]},
            {"$set": {"failedResetAttempts": 3}},
        )
        token = _plant_valid_token(db, company["companyId"])
        service.reset_password(token, NEW_PASS, CONFIRM_PASS, secret_key=SECRET_KEY)
        updated = db["companies"].find_one({"companyId": company["companyId"]})
        assert updated.get("failedResetAttempts") is None

    def test_new_password_is_hashed_in_db(self, db, service, company):
        from app.services.auth_service import verify_password
        token = _plant_valid_token(db, company["companyId"])
        service.reset_password(token, NEW_PASS, CONFIRM_PASS, secret_key=SECRET_KEY)
        updated = db["companies"].find_one({"companyId": company["companyId"]})
        assert verify_password(NEW_PASS, updated["passwordHash"])

    def test_reset_token_cleared_after_use(self, db, service, company):
        token = _plant_valid_token(db, company["companyId"])
        service.reset_password(token, NEW_PASS, CONFIRM_PASS, secret_key=SECRET_KEY)
        updated = db["companies"].find_one({"companyId": company["companyId"]})
        assert updated.get("passwordReset") is None


class TestExpiredToken:
    def test_expired_token_rejected(self, db, service, company):
        token = _plant_expired_token(db, company["companyId"])
        result = service.reset_password(token, NEW_PASS, CONFIRM_PASS)
        assert result["success"] is False
        assert "expired" in result["message"].lower() or "invalid" in result["message"].lower()

    def test_expired_token_clears_reset_field(self, db, service, company):
        token = _plant_expired_token(db, company["companyId"])
        service.reset_password(token, NEW_PASS, CONFIRM_PASS)
        updated = db["companies"].find_one({"companyId": company["companyId"]})
        assert updated.get("passwordReset") is None


class TestInvalidToken:
    def test_random_token_rejected(self, db, service, company):
        result = service.reset_password("totally-invalid-token", NEW_PASS, CONFIRM_PASS)
        assert result["success"] is False

    def test_empty_token_rejected(self, db, service):
        result = service.reset_password("", NEW_PASS, CONFIRM_PASS)
        assert result["success"] is False
        assert "required" in result["message"].lower()

    def test_tampered_token_rejected(self, db, service, company):
        token = _plant_valid_token(db, company["companyId"])
        # Flip one character in the token
        tampered = token[:-1] + ("Z" if token[-1] != "Z" else "A")
        result = service.reset_password(tampered, NEW_PASS, CONFIRM_PASS)
        assert result["success"] is False


class TestRateLimiting:
    """Tests use the Flask app context for company_routes rate limiting."""

    def test_rate_limit_enforced_at_route_level(self):
        """Verify the Mongo rate-limit bucket logic (unit test)."""
        from app.routes.company_routes import _consume_rate_limit_bucket, _rate_limit_key
        db = _make_db()
        collection = db["password_reset_rate_limits"]
        key = _rate_limit_key("ip", "user@test.com", "10.0.0.1")

        # Fill the bucket (max 3)
        for _ in range(3):
            limited, _ = _consume_rate_limit_bucket(
                collection, key=key, max_attempts=3, window_minutes=15,
                ip_address="10.0.0.1", user_agent="pytest",
            )
        # 4th attempt should be limited
        limited, retry = _consume_rate_limit_bucket(
            collection, key=key, max_attempts=3, window_minutes=15,
            ip_address="10.0.0.1", user_agent="pytest",
        )
        assert limited is True
        assert retry > 0


class TestEmailSendFailure:
    def test_generic_success_returned_even_on_email_failure(self, db, service, company):
        """
        The forgot-password endpoint must return a generic success even when
        SMTP fails — prevents account enumeration.
        """
        email_svc = _make_email_service(should_fail=True)
        result = service.request_password_reset(
            email="test@example.com",
            email_service=email_svc,
            frontend_base_url="http://localhost:5173",
            token_expiry_minutes=30,
        )
        # Generic message — no enumeration leak regardless of email outcome
        assert result["success"] is True
        assert "password reset link" in result["message"].lower()

    def test_email_failure_logged_in_db(self, db, service, company):
        email_svc = _make_email_service(should_fail=True)
        service.request_password_reset(
            email="test@example.com",
            email_service=email_svc,
            frontend_base_url="http://localhost:5173",
            token_expiry_minutes=30,
        )
        log = db["password_reset_audit_logs"].find_one({"outcome": "email-send-failed"})
        assert log is not None


class TestPasswordHistory:
    def test_reusing_old_password_rejected(self, db, service, company):
        # First reset: set to NEW_PASS
        token = _plant_valid_token(db, company["companyId"])
        service.reset_password(token, NEW_PASS, CONFIRM_PASS, password_history_size=5)

        # Second reset: try to reuse OLD password
        token2 = _plant_valid_token(db, company["companyId"])
        result = service.reset_password(
            token2, NEW_PASS, NEW_PASS, password_history_size=5
        )
        assert result["success"] is False
        assert "reuse" in result["message"].lower() or "reused" in result["message"].lower()

    def test_different_password_accepted(self, db, service, company):
        token = _plant_valid_token(db, company["companyId"])
        service.reset_password(token, NEW_PASS, CONFIRM_PASS, password_history_size=5)
        token2 = _plant_valid_token(db, company["companyId"])
        result = service.reset_password(
            token2, "AnotherPass@789", "AnotherPass@789", password_history_size=5
        )
        assert result["success"] is True


class TestSuccessfulResetAndLogin:
    def test_can_login_with_new_password_after_reset(self, db, service, company):
        token = _plant_valid_token(db, company["companyId"])
        service.reset_password(token, NEW_PASS, CONFIRM_PASS, secret_key=SECRET_KEY)
        login_result = service.login_company("test@example.com", NEW_PASS)
        assert login_result["success"] is True

    def test_old_password_rejected_after_reset(self, db, service, company):
        token = _plant_valid_token(db, company["companyId"])
        service.reset_password(token, NEW_PASS, CONFIRM_PASS)
        login_result = service.login_company("test@example.com", "OldPass@123")
        assert login_result["success"] is False

    def test_audit_log_created_on_success(self, db, service, company):
        token = _plant_valid_token(db, company["companyId"])
        service.reset_password(token, NEW_PASS, CONFIRM_PASS)
        log = db["password_reset_audit_logs"].find_one({
            "event": "password_reset_completed",
            "outcome": "success",
        })
        assert log is not None


class TestPasswordPolicy:
    def test_short_password_rejected(self, db, service, company):
        token = _plant_valid_token(db, company["companyId"])
        result = service.reset_password(token, "Ab1!", "Ab1!")
        assert result["success"] is False

    def test_no_uppercase_rejected(self, db, service, company):
        token = _plant_valid_token(db, company["companyId"])
        result = service.reset_password(token, "nouppercase1!", "nouppercase1!")
        assert result["success"] is False

    def test_no_special_char_rejected(self, db, service, company):
        token = _plant_valid_token(db, company["companyId"])
        result = service.reset_password(token, "NoSpecial123", "NoSpecial123")
        assert result["success"] is False

    def test_passwords_must_match(self, db, service, company):
        token = _plant_valid_token(db, company["companyId"])
        result = service.reset_password(token, NEW_PASS, "DifferentPass@999")
        assert result["success"] is False
        assert "match" in result["message"].lower()
