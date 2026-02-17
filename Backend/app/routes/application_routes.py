import os
import logging
from flask import Blueprint, current_app, jsonify, request, send_file

from ..services.application_service import ApplicationService
from ..services.pipeline_service import PipelineService
from ..services.storage_service import StorageService
from ..services.email_service import EmailService
from ..services.job_service import JobService

application_bp = Blueprint("application", __name__)
logger = logging.getLogger(__name__)


def _assign_ranks(items):
    grouped = {}
    for item in items:
        key = item.get("jobId") or item.get("jobTitle")
        grouped.setdefault(key, []).append(item)

    for group in grouped.values():
        scored = [i for i in group if isinstance(i.get("score"), (int, float))]
        scored.sort(key=lambda x: x.get("score", 0), reverse=True)
        for idx, entry in enumerate(scored, start=1):
            entry["rank"] = idx
        for entry in group:
            entry.setdefault("rank", None)

    return items


@application_bp.route("/apply", methods=["POST"])
def apply_for_job():
    form = request.form
    job_id = form.get("jobId")
    resume_file = request.files.get("resume")

    if not job_id or not resume_file:
        return jsonify({"success": False, "message": "jobId and resume are required"}), 400

    ext = os.path.splitext(resume_file.filename or "")[1].lower()
    if ext not in current_app.config["ALLOWED_RESUME_EXTENSIONS"]:
        return jsonify({"success": False, "message": "Only PDF resumes are supported"}), 400

    candidate = {
        "fullName": form.get("fullName", ""),
        "email": form.get("email", ""),
        "phone": form.get("phone", ""),
        "degree": form.get("degree", ""),
        "branch": form.get("branch", ""),
    }

    storage = StorageService(current_app.config["UPLOADS_DIR"], current_app.config["TMP_DIR"])
    email = EmailService(
        current_app.config["SMTP_HOST"],
        current_app.config["SMTP_PORT"],
        current_app.config["SMTP_USER"],
        current_app.config["SMTP_PASSWORD"],
        current_app.config["SMTP_FROM"],
        current_app.config["SMTP_TLS"],
    )
    pipeline = PipelineService(
        storage,
        email,
        project_root=current_app.config["PROJECT_ROOT"],
        score_threshold=current_app.config["SCORE_THRESHOLD"],
    )
    app_service = ApplicationService(current_app.mongo_db, pipeline)

    job_service = JobService(current_app.mongo_db, None)
    job = job_service.get_job(job_id)
    if not job:
        return jsonify({"success": False, "message": "Job not found"}), 404

    if not job.get("companyEmail"):
        company = current_app.mongo_db["companies"].find_one(
            {"companyId": job.get("companyId")},
            {"email": 1, "_id": 0}
        )
        if company and company.get("email"):
            job["companyEmail"] = company.get("email")

    try:
        application = app_service.create_application(job, candidate, resume_file)
        return jsonify({
            "success": True,
            "message": (
                f"Application submitted successfully for {job.get('title', 'this role')} at "
                f"{job.get('companyName', 'the company')}. "
                "We are reviewing your profile. If you are shortlisted, "
                "we will contact you by email with the next steps."
            ),
            "applicationId": application.get("applicationId"),
            "status": application.get("status"),
            "score": application.get("score"),
        })
    except Exception as exc:
        logger.exception("Application processing failed")
        return jsonify({"success": False, "message": str(exc)}), 500


@application_bp.route("/company/<company_id>/resumes", methods=["GET"])
def list_company_resumes(company_id):
    app_service = ApplicationService(current_app.mongo_db)
    resumes = app_service.list_company_resumes(company_id)

    formatted = [
        {
            "jobId": item.get("jobId"),
            "candidateName": item.get("candidateName"),
            "resumeName": item.get("resumeName"),
            "email": item.get("email"),
            "jobTitle": item.get("jobTitle"),
            "status": item.get("status"),
            "score": item.get("score"),
            "resumeUrl": f"/api/resumes/{item.get('applicationId')}",
        }
        for item in resumes
    ]
    _assign_ranks(formatted)

    return jsonify(formatted)


@application_bp.route("/company/<company_id>/history", methods=["GET"])
def list_company_history(company_id):
    app_service = ApplicationService(current_app.mongo_db)
    history = app_service.list_company_history(company_id)

    formatted = []
    for item in history:
        resume_url = f"/api/resumes/{item.get('applicationId')}"
        formatted.append({
            "jobId": item.get("jobId"),
            "candidateName": item.get("candidateName"),
            "jobTitle": item.get("jobTitle"),
            "status": item.get("status"),
            "date": item.get("createdAt"),
            "score": item.get("score"),
            "email": item.get("email"),
            "resumeUrl": resume_url,
        })
    _assign_ranks(formatted)

    return jsonify(formatted)


@application_bp.route("/resumes/<application_id>", methods=["GET"])
def download_resume(application_id):
    app_doc = current_app.mongo_db["applications"].find_one({"applicationId": application_id})
    if not app_doc:
        return jsonify({"message": "Resume not found"}), 404

    resume_path = app_doc.get("resumePdfPath")
    if not resume_path or not os.path.exists(resume_path):
        return jsonify({"message": "Resume file missing"}), 404

    return send_file(resume_path, as_attachment=True)
