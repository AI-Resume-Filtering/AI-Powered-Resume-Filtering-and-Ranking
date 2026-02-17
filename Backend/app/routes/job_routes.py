from flask import Blueprint, current_app, jsonify, request
import os

from ..services.company_service import CompanyService
from ..services.job_service import JobService
from ..services.storage_service import StorageService

job_bp = Blueprint("job", __name__)


@job_bp.route("/jobs", methods=["GET"])
def list_jobs():
    service = JobService(current_app.mongo_db, None)
    jobs = service.list_jobs()
    formatted = [
        {
            "id": job.get("jobId"),
            "title": job.get("title"),
            "companyName": job.get("companyName"),
            "companyRegNo": job.get("companyRegNo"),
            "location": job.get("location", ""),
            "experience": job.get("experience", ""),
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
def post_job():
    company_id = request.form.get("companyId")
    job_title = request.form.get("jobTitle")
    jd_file = request.files.get("descriptionPdf")

    if not company_id or not job_title or not jd_file:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    ext = os.path.splitext(jd_file.filename or "")[1].lower()
    if ext not in current_app.config["ALLOWED_JD_EXTENSIONS"]:
        return jsonify({"success": False, "message": "Only PDF job descriptions are supported"}), 400

    company_service = CompanyService(current_app.mongo_db)
    company = company_service.collection.find_one({"companyId": company_id})
    if not company:
        return jsonify({"success": False, "message": "Company not found"}), 404

    storage = StorageService(current_app.config["UPLOADS_DIR"], current_app.config["TMP_DIR"])
    service = JobService(current_app.mongo_db, storage)

    job = service.create_job(company, job_title, jd_file)

    return jsonify({"success": True, "jobId": job.get("jobId")})


@job_bp.route("/company/<company_id>/jobs", methods=["GET"])
def list_company_jobs(company_id):
    job_service = JobService(current_app.mongo_db, None)
    jobs = job_service.list_company_jobs(company_id)

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
            "totalApplications": total_applications,
        })

    return jsonify(formatted)


@job_bp.route("/company/delete-job", methods=["DELETE"])
def delete_job():
    payload = request.get_json(silent=True) or {}
    job_id = payload.get("jobId")
    if not job_id:
        return jsonify({"success": False, "message": "jobId is required"}), 400

    service = JobService(current_app.mongo_db, None)
    deleted = service.delete_job(job_id)
    if not deleted:
        return jsonify({"success": False, "message": "Job not found"}), 404

    return jsonify({"success": True})


