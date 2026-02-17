import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = BASE_DIR.parent
PROJECT_ROOT = BACKEND_ROOT.parent

INSTANCE_DIR = BACKEND_ROOT / "instance"
STORAGE_DIR = INSTANCE_DIR / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
TMP_DIR = STORAGE_DIR / "tmp"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")

    PROJECT_ROOT = str(PROJECT_ROOT)

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB = os.getenv("MONGO_DB", "resume_filtering")

    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM = os.getenv("SMTP_FROM", "")
    SMTP_TLS = os.getenv("SMTP_TLS", "true").lower() == "true"

    SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", "70"))

    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "20971520"))

    STORAGE_DIR = str(STORAGE_DIR)
    UPLOADS_DIR = str(UPLOADS_DIR)
    TMP_DIR = str(TMP_DIR)

    ALLOWED_RESUME_EXTENSIONS = {".pdf"}
    ALLOWED_JD_EXTENSIONS = {".pdf"}
