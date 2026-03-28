import os

# Guard against OpenBLAS initialization failures across all startup paths.
for env_var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(env_var, "1")

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from .extensions import init_mongo
from .routes import register_blueprints
from .utils.logging import configure_logging
from .utils.email_queue import init_email_queue
from .utils.ttl_indexes import ensure_indexes
from .utils.secrets import init_key_vault


def create_app():
    load_dotenv()
    from .config import Config

    configure_logging()

    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for frontend access
    # CORS_ORIGINS env var overrides defaults for production (comma-separated list)
    raw_origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:5174,http://localhost:3000,"
        "http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:3000"
    )
    allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
    CORS(
        app,
        origins=allowed_origins,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=True,
    )

    init_mongo(app)
    register_blueprints(app)

    # ── optional infrastructure ───────────────────────────────────────────────
    # Background email queue (uses a daemon thread — no extra processes needed)
    if app.config.get("EMAIL_QUEUE_ENABLED", True):
        init_email_queue(enabled=True)

    # MongoDB TTL + query indexes
    try:
        ensure_indexes(
            app.mongo_db,
            audit_ttl_days=int(app.config.get("AUDIT_LOG_TTL_DAYS", 90)),
            rate_limit_ttl_days=int(app.config.get("RATE_LIMIT_TTL_DAYS", 7)),
        )
    except Exception:
        app.logger.warning("Could not ensure database indexes at startup", exc_info=True)

    # Azure Key Vault (no-op when AZURE_KEY_VAULT_URL is not set or SDK not installed)
    init_key_vault(app.config.get("AZURE_KEY_VAULT_URL", ""))

    @app.after_request
    def add_cors_headers(response):
        request_origin = request.headers.get("Origin", "")
        if request_origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = request_origin
            response.headers["Vary"] = "Origin"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"success": False, "message": "Endpoint not found. Use /api/health or /api/..."}), 404

    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.exception("Unhandled error")
        return jsonify({"success": False, "message": "Internal server error"}), 500

    return app
