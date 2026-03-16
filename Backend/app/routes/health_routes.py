from flask import Blueprint, current_app, jsonify

from ..extensions import is_mongo_available

health_bp = Blueprint("health", __name__)


@health_bp.route("/", methods=["GET"])
def root():
    return jsonify({
        "service": "AI Resume Filtering Backend API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "company": "/api/company",
            "jobs": "/api/jobs",
            "apply": "/api/apply"
        }
    })


@health_bp.route("/api/health", methods=["GET"])
def health_check():
    db_ok = is_mongo_available(current_app)
    if db_ok:
        return jsonify({
            "status": "ok",
            "database": {
                "connected": True,
                "message": "MongoDB reachable",
            },
        }), 200

    return jsonify({
        "status": "degraded",
        "database": {
            "connected": False,
            "message": current_app.mongo_error or "MongoDB unavailable",
        },
    }), 503
