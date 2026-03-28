from flask import Blueprint, current_app, jsonify, request
import logging
import os

from ..services.company_service import CompanyService
from ..services.job_service import JobService
from ..services.storage_service import StorageService
from ..utils.auth_middleware import require_auth
from ..utils.validators import validate_job_post

job_bp = Blueprint("job", __name__)
logger = logging.getLogger(__name__)


@job_bp.route("/jobs", methods=["GET"])
def list_jobs():
    # A6: pagination support
    try:
        page = max(int(request.args.get("page", 1)), 1)
        limit = min(int(request.args.get("limit", 50)), 200)
    except (TypeError, ValueError):
        page, limit = 1, 50

    query = (request.args.get("q", "") or "").strip()
    sort = (request.args.get("sort", "newest") or "newest").strip().lower()
    try:
        posted_within_days = request.args.get("postedWithinDays")
        posted_within_days = int(posted_within_days) if posted_within_days else None
    except (TypeError, ValueError):
        posted_within_days = None

    service = JobService(current_app.mongo_db, None)
    jobs = service.list_jobs(
        page=page,
        limit=limit,
        query=query,
        sort=sort,
        posted_within_days=posted_within_days,
    )
    formatted = [
        {
            "id": job.get("jobId"),
            "title": job.get("title"),
            "companyName": job.get("companyName"),
            "companyRegNo": job.get("companyRegNo"),
            "location": job.get("location", ""),
            "experience": job.get("experience", ""),
            "postDate": job.get("postDate"),
            "createdAt": job.get("createdAt"),
        }
        for job in jobs
    ]
    return jsonify(formatted)


@job_bp.route("/jobs/<job_id>", methods=["GET"])
def get_job(job_id):
    service = JobService(current_app.mongo_db, None)
    job = service.get_job(job_id)
    if not job:
        return jsonify({"message": "Job not found"}), 404

    return jsonify({
        "id": job.get("jobId"),
        "title": job.get("title"),
        "description": job.get("description", ""),
        "companyName": job.get("companyName"),
    })


@job_bp.route("/company/post-job", methods=["POST"])
@require_auth  # S4: auth required
def post_job():
    company_id = request.form.get("companyId")

    # S4/IDOR: posted companyId must match authenticated company
    if company_id != request.auth_company_id:
        return jsonify({"success": False, "message": "Access denied"}), 403

    job_title = request.form.get("jobTitle")
    jd_file = request.files.get("descriptionPdf")

    if not company_id or not job_title or not jd_file:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    # S5: Validate job title
    validation_errors = validate_job_post(request.form)
    if validation_errors:
        return jsonify({"success": False, "message": "; ".join(validation_errors)}), 400

    ext = os.path.splitext(jd_file.filename or "")[1].lower()
    if ext not in current_app.config["ALLOWED_JD_EXTENSIONS"]:
        return jsonify({"success": False, "message": "Only PDF job descriptions are supported"}), 400

    company_service = CompanyService(current_app.mongo_db)
    company = company_service.collection.find_one({"companyId": company_id})
    if not company:
        return jsonify({"success": False, "message": "Company not found"}), 404

    storage = StorageService(current_app.config["UPLOADS_DIR"], current_app.config["TMP_DIR"])
    service = JobService(current_app.mongo_db, storage)

    try:
        job = service.create_job(company, job_title, jd_file)
        return jsonify({"success": True, "jobId": job.get("jobId")})
    except Exception:
        logger.exception("Failed to post job")
        return jsonify({"success": False, "message": "Failed to post job due to a server error"}), 500


@job_bp.route("/company/<company_id>/jobs", methods=["GET"])
@require_auth  # S4: auth required + IDOR check in decorator
def list_company_jobs(company_id):
    # A6: pagination
    try:
        page = max(int(request.args.get("page", 1)), 1)
        limit = min(int(request.args.get("limit", 50)), 200)
    except (TypeError, ValueError):
        page, limit = 1, 50

    job_service = JobService(current_app.mongo_db, None)
    jobs = job_service.list_company_jobs(company_id, page=page, limit=limit)

    applications = current_app.mongo_db["applications"]
    formatted = []
    for job in jobs:
        total_applications = applications.count_documents({"jobId": job.get("jobId")})
        formatted.append({
            "jobId": job.get("jobId"),
            "title": job.get("title"),
            "description": job.get("description", ""),
            "postDate": job.get("postDate"),
            "createdAt": job.get("createdAt"),
            "status": job.get("status", "active"),  # A4: job lifecycle
            "totalApplications": total_applications,
        })

    return jsonify(formatted)


@job_bp.route("/company/delete-job", methods=["DELETE"])
@require_auth  # S4: auth required
def delete_job():
    payload = request.get_json(silent=True) or {}
    job_id = payload.get("jobId")
    if not job_id:
        return jsonify({"success": False, "message": "jobId is required"}), 400

    service = JobService(current_app.mongo_db, None)
    job = service.get_job(job_id)
    if not job:
        return jsonify({"success": False, "message": "Job not found"}), 404

    # S4/IDOR: only the owning company can delete their job
    if job.get("companyId") != request.auth_company_id:
        return jsonify({"success": False, "message": "Access denied"}), 403

    # L2: delete job + its orphaned applications
    deleted = service.delete_job(job_id)
    if not deleted:
        return jsonify({"success": False, "message": "Job not found"}), 404

    return jsonify({"success": True})


