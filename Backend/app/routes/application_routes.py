import os
import re
import threading
import logging
import uuid
from datetime import datetime
from flask import Blueprint, current_app, jsonify, request, send_file

from ..services.application_service import ApplicationService
from ..services.pipeline_service import PipelineService
from ..services.storage_service import StorageService
from ..services.email_service import EmailService
from ..services.job_service import JobService
from ..utils.auth_middleware import require_auth
from ..utils.validators import validate_candidate_form

application_bp = Blueprint("application", __name__)
logger = logging.getLogger(__name__)


def _display_resume_name(filename):
    """Strip generated UUID prefixes so admins see the original upload name."""
    base_name = os.path.basename(filename or "")
    return re.sub(r"^[0-9a-fA-F]{32}_", "", base_name)


def _assign_ranks(items):
    """Dynamically rank candidates per job by score at read time."""
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


def _run_pipeline_in_background(flask_app, db, pipeline, job, candidate, resume_pdf_path, application_id):
    """Background thread: run NLP+AI pipeline then update the DB record."""
    with flask_app.app_context():
        try:
            result = pipeline.run_from_path(job, candidate, resume_pdf_path)
            # L3: use the saved filename (not the original browser filename)
            db["applications"].update_one(
                {"applicationId": application_id},
                {"$set": {
                    "score": result["score"],
                    "status": result["status"],
                    "emailSent": result["emailSent"],
                    "nlpOutputPath": result.get("nlpOutputPath"),
                    "resumeTextPath": result.get("resumeTextPath"),
                    "resumeName": os.path.basename(resume_pdf_path),
                }}
            )
            logger.info("Pipeline completed for application %s — status: %s", application_id, result["status"])
        except Exception:
            logger.exception("Background pipeline failed for application %s", application_id)
            db["applications"].update_one(
                {"applicationId": application_id},
                {"$set": {"status": "error"}}
            )


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

    # S5: validate candidate form fields
    validation_errors = validate_candidate_form(form)
    if validation_errors:
        return jsonify({"success": False, "message": "; ".join(validation_errors)}), 400

    candidate = {
        "fullName": form.get("fullName", "").strip(),
        "email": form.get("email", "").strip(),
        "phone": form.get("phone", "").strip(),
        "degree": form.get("degree", "").strip(),
        "branch": form.get("branch", "").strip(),
    }

    job_service = JobService(current_app.mongo_db, None)
    job = job_service.get_job(job_id)
    if not job:
        return jsonify({"success": False, "message": "Job not found"}), 404

    if not job.get("companyEmail"):
        company = current_app.mongo_db["companies"].find_one(
            {"companyId": job.get("companyId")}, {"email": 1, "_id": 0}
        )
        if company and company.get("email"):
            job["companyEmail"] = company["email"]

    # L1: Prevent duplicate applications (same email + same job)
    existing = current_app.mongo_db["applications"].find_one({
        "jobId": job_id,
        "email": candidate["email"],
        "status": {"$in": ["processing", "Selected", "Rejected"]},
    })
    if existing:
        return jsonify({
            "success": False,
            "message": "You have already applied for this position.",
        }), 409

    storage = StorageService(current_app.config["UPLOADS_DIR"], current_app.config["TMP_DIR"])

    # Save file to disk synchronously — file object can't be used after request ends
    try:
        resume_pdf_path = storage.save_upload(resume_file, "resumes")
    except Exception:
        logger.exception("Failed to save resume file")
        return jsonify({"success": False, "message": "Could not save resume. Please try again."}), 500

    application_id = uuid.uuid4().hex
    candidate["applicationId"] = application_id

    # Insert initial "processing" record (A3: async pipeline)
    initial_app = {
        "applicationId": application_id,
        "jobId": job_id,
        "jobTitle": job.get("title"),
        "companyId": job.get("companyId"),
        "companyRegNo": job.get("companyRegNo"),
        "candidateName": candidate["fullName"],
        "email": candidate["email"],
        "phone": candidate["phone"],
        "degree": candidate["degree"],
        "branch": candidate["branch"],
        # L3: resumeName will be updated after pipeline saves the file
        "resumeName": os.path.basename(resume_pdf_path),
        "resumePdfPath": resume_pdf_path,
        "status": "processing",
        "score": None,
        "rank": None,  # L4: rank is always computed at read time by _assign_ranks
        "emailSent": False,
        "createdAt": datetime.utcnow().isoformat(),
    }
    current_app.mongo_db["applications"].insert_one(initial_app)

    email_svc = EmailService(
        current_app.config["SMTP_HOST"],
        current_app.config["SMTP_PORT"],
        current_app.config["SMTP_USER"],
        current_app.config["SMTP_PASSWORD"],
        current_app.config["SMTP_FROM"],
        current_app.config["SMTP_TLS"],
    )
    pipeline = PipelineService(
        storage,
        email_svc,
        project_root=current_app.config["PROJECT_ROOT"],
        score_threshold=current_app.config["SCORE_THRESHOLD"],
        db=current_app.mongo_db,
    )

    # A3: Run heavy pipeline in a background thread
    flask_app = current_app._get_current_object()
    db = current_app.mongo_db
    thread = threading.Thread(
        target=_run_pipeline_in_background,
        args=(flask_app, db, pipeline, job, candidate, resume_pdf_path, application_id),
        daemon=True,
    )
    thread.start()

    return jsonify({
        "success": True,
        "applicationId": application_id,
        "status": "processing",
        "message": (
            f"Application submitted for {job.get('title', 'this role')} at "
            f"{job.get('companyName', 'the company')}. "
            "Your resume is being analysed. Check your application status shortly."
        ),
    }), 202


@application_bp.route("/apply/status/<application_id>", methods=["GET"])
def get_application_status(application_id):
    """A3: Polling endpoint so the frontend can track async processing."""
    app_doc = current_app.mongo_db["applications"].find_one(
        {"applicationId": application_id},
        {"_id": 0, "applicationId": 1, "status": 1},
    )
    if not app_doc:
        return jsonify({"success": False, "message": "Application not found"}), 404

    return jsonify({
        "success": True,
        "applicationId": application_id,
        "status": app_doc.get("status"),
    })


@application_bp.route("/company/<company_id>/resumes", methods=["GET"])
@require_auth  # S4: auth + IDOR guard
def list_company_resumes(company_id):
    # A6: pagination
    try:
        page = max(int(request.args.get("page", 1)), 1)
        limit = min(int(request.args.get("limit", 100)), 500)
    except (TypeError, ValueError):
        page, limit = 1, 100

    app_service = ApplicationService(current_app.mongo_db)
    resumes = app_service.list_company_resumes(company_id, page=page, limit=limit)

    formatted = [
        {
            "applicationId": item.get("applicationId"),
            "jobId": item.get("jobId"),
            "candidateName": item.get("candidateName"),
            # L3: resumeName is now the saved basename set by the pipeline
            "resumeName": _display_resume_name(item.get("resumeName")),
            "email": item.get("email"),
            "jobTitle": item.get("jobTitle"),
            "status": item.get("status") or "unknown",  # L6: null guard
            "score": item.get("score"),
            "resumeUrl": f"/api/resumes/{item.get('applicationId')}",
        }
        for item in resumes
    ]
    _assign_ranks(formatted)

    return jsonify(formatted)


@application_bp.route("/company/<company_id>/history", methods=["GET"])
@require_auth  # S4: auth + IDOR guard
def list_company_history(company_id):
    # A6: pagination
    try:
        page = max(int(request.args.get("page", 1)), 1)
        limit = min(int(request.args.get("limit", 100)), 500)
    except (TypeError, ValueError):
        page, limit = 1, 100

    app_service = ApplicationService(current_app.mongo_db)
    history = app_service.list_company_history(company_id, page=page, limit=limit)

    formatted = []
    for item in history:
        formatted.append({
            "applicationId": item.get("applicationId"),
            "jobId": item.get("jobId"),
            "candidateName": item.get("candidateName"),
            "jobTitle": item.get("jobTitle"),
            "status": item.get("status") or "unknown",  # L6: null guard
            "date": item.get("createdAt"),
            "score": item.get("score"),
            "email": item.get("email"),
            "resumeUrl": f"/api/resumes/{item.get('applicationId')}",
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
