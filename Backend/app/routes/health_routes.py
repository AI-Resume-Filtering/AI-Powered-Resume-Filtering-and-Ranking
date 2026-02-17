from flask import Blueprint, jsonify

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
    return jsonify({"status": "ok"})
