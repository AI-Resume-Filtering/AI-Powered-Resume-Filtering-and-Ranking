import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = BASE_DIR.parent
PROJECT_ROOT = BACKEND_ROOT

INSTANCE_DIR = BACKEND_ROOT / "instance"
STORAGE_DIR = INSTANCE_DIR / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
TMP_DIR = STORAGE_DIR / "tmp"


# Keys that are obviously placeholder / insecure
_WEAK_KEYS = {
    "dev", "secret", "changeme", "change-this",
    "change-this-to-a-long-random-string-before-deploying",
}


def _load_secret_key() -> str:
    key = os.getenv("SECRET_KEY", "")
    flask_env = os.getenv("FLASK_ENV", "production")
    if not key or len(key) < 32 or key in _WEAK_KEYS:
        if flask_env == "production" and os.getenv("FLASK_DEBUG", "0") != "1":
            raise RuntimeError(
                "SECRET_KEY must be a strong random value (32+ chars). "
                "Set it in Backend/.env before running in production."
            )
        import logging as _log
        _log.warning(
            "SECRET_KEY is weak or missing — safe for development only. "
            "Set a strong SECRET_KEY in .env before deploying."
        )
        if not key:
            key = "dev-unsafe-key-please-set-SECRET_KEY-in-dotenv-file"
    return key


class Config:
    SECRET_KEY = _load_secret_key()

    PROJECT_ROOT = str(PROJECT_ROOT)

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB = os.getenv("MONGO_DB", "resume_filtering")
    MONGO_SERVER_SELECTION_TIMEOUT_MS = int(os.getenv("MONGO_SERVER_SELECTION_TIMEOUT_MS", "3000"))
    MONGO_CONNECT_TIMEOUT_MS = int(os.getenv("MONGO_CONNECT_TIMEOUT_MS", "3000"))
    MONGO_SOCKET_TIMEOUT_MS = int(os.getenv("MONGO_SOCKET_TIMEOUT_MS", "5000"))

    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM = os.getenv("SMTP_FROM", "")
    SMTP_TLS = os.getenv("SMTP_TLS", "true").lower() == "true"

    FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")
    PASSWORD_RESET_TOKEN_EXP_MINUTES = int(os.getenv("PASSWORD_RESET_TOKEN_EXP_MINUTES", "30"))
    PASSWORD_RESET_RATE_LIMIT_WINDOW_MINUTES = int(os.getenv("PASSWORD_RESET_RATE_LIMIT_WINDOW_MINUTES", "15"))
    PASSWORD_RESET_RATE_LIMIT_MAX_ATTEMPTS_PER_EMAIL_IP = int(
        os.getenv("PASSWORD_RESET_RATE_LIMIT_MAX_ATTEMPTS_PER_EMAIL_IP", "5")
    )
    PASSWORD_RESET_RATE_LIMIT_MAX_ATTEMPTS_PER_IP = int(
        os.getenv("PASSWORD_RESET_RATE_LIMIT_MAX_ATTEMPTS_PER_IP", "20")
    )

    APP_NAME = os.getenv("APP_NAME", "Resume Filtering Platform")
    APP_LOGO_URL = os.getenv("APP_LOGO_URL", "")
    SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", SMTP_FROM)

    SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", "70"))
    FEEDBACK_RETRAIN_THRESHOLD = int(os.getenv("FEEDBACK_RETRAIN_THRESHOLD", "50"))
    FEEDBACK_MIN_TRAIN_SAMPLES = int(os.getenv("FEEDBACK_MIN_TRAIN_SAMPLES", "20"))

    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "20971520"))

    STORAGE_DIR = str(STORAGE_DIR)
    UPLOADS_DIR = str(UPLOADS_DIR)
    TMP_DIR = str(TMP_DIR)

    ALLOWED_RESUME_EXTENSIONS = {".pdf"}
    ALLOWED_JD_EXTENSIONS = {".pdf"}

    # -- Admin panel ---------------------------------------------------------------
    # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
    ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")
    ADMIN_ALERT_EMAIL = os.getenv("ADMIN_ALERT_EMAIL", "")

    # -- Redis (optional) ----------------------------------------------------------
    # Required for Redis-based rate limiting and background email queue.
    # Falls back gracefully when not set.
    REDIS_URL = os.getenv("REDIS_URL", "")

    # -- reCAPTCHA v2 (optional) ---------------------------------------------------
    # Get keys at https://www.google.com/recaptcha/admin
    RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY", "")
    RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"

    # -- Password history ----------------------------------------------------------
    PASSWORD_HISTORY_SIZE = int(os.getenv("PASSWORD_HISTORY_SIZE", "5"))

    # -- Account lock --------------------------------------------------------------
    MAX_FAILED_RESETS_BEFORE_LOCK = int(os.getenv("MAX_FAILED_RESETS_BEFORE_LOCK", "10"))
    ACCOUNT_LOCK_DURATION_MINUTES = int(os.getenv("ACCOUNT_LOCK_DURATION_MINUTES", "60"))

    # -- TTL cleanup ---------------------------------------------------------------
    AUDIT_LOG_TTL_DAYS = int(os.getenv("AUDIT_LOG_TTL_DAYS", "90"))
    RATE_LIMIT_TTL_DAYS = int(os.getenv("RATE_LIMIT_TTL_DAYS", "7"))

    # -- Background email queue ----------------------------------------------------
    EMAIL_QUEUE_ENABLED = os.getenv("EMAIL_QUEUE_ENABLED", "true").lower() == "true"

    # -- Production domain (overrides localhost link-building) ---------------------
    # Example: https://app.yourcompany.com
    APP_DOMAIN = os.getenv("APP_DOMAIN", "")

    # -- Azure Key Vault (optional) ------------------------------------------------
    # Set AZURE_KEY_VAULT_URL to enable secret retrieval from Key Vault.
    AZURE_KEY_VAULT_URL = os.getenv("AZURE_KEY_VAULT_URL", "")
