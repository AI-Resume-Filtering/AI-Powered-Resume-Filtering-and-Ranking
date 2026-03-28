"""
Feedback Routes - API endpoints for collecting recruiter feedback for self-learning system.

Endpoints:
  POST   /api/feedback              - Save recruiter feedback
  GET    /api/feedback              - Retrieve feedback records
  GET    /api/feedback/stats        - Get feedback statistics
  DELETE /api/feedback/:resume/:job - Delete incorrect feedback
"""

import logging
from flask import Blueprint, current_app, jsonify, request

from ..services.feedback_service import FeedbackService
from ..utils.auth_middleware import require_auth

feedback_bp = Blueprint("feedback", __name__)
logger = logging.getLogger(__name__)


@feedback_bp.route("/feedback", methods=["POST"])
@require_auth
def save_feedback():
    """
    Save recruiter feedback for a candidate-job pair.
    
    This endpoint collects feedback when recruiters accept or reject candidates.
    The feedback is used to:
      1. Build ML training dataset
      2. Automatically retrain model when threshold is reached
      3. Improve future candidate rankings
    
    Request format:
    {
        "resumeId": "string (required)",
        "jobId": "string (required)",
        "semanticScore": float (required, 0-1 or 0-100),
        "experienceScore": float (required, 0-100),
        "educationScore": float (required, 0-100),
        "selected": boolean (required),
        "recruiterNotes": "string (optional)",
        "userId": "string (optional, user ID of recruiter)"
    }
    
    Response (success):
    {
        "success": true,
        "message": "Feedback saved successfully",
        "retraining": {
            "triggered": false,
            "feedbackCount": 45,
            "reason": "threshold-not-met"
        }
    }
    
    Response (error):
    {
        "success": false,
        "message": "Error message here"
    }
    """
    try:
        data = request.get_json() or {}

        # Extract and validate required fields
        resume_id = data.get("resumeId", "").strip()
        job_id = data.get("jobId", "").strip()
        semantic_score = data.get("semanticScore")
        experience_score = data.get("experienceScore")
        education_score = data.get("educationScore")
        selected = data.get("selected")
        recruiter_notes = data.get("recruiterNotes", "").strip()
        user_id = data.get("userId", "").strip()

        # Validation
        if not resume_id:
            return jsonify({
                "success": False,
                "message": "resumeId is required",
            }), 400

        if not job_id:
            return jsonify({
                "success": False,
                "message": "jobId is required",
            }), 400

        if semantic_score is None:
            return jsonify({
                "success": False,
                "message": "semanticScore is required",
            }), 400

        if experience_score is None:
            return jsonify({
                "success": False,
                "message": "experienceScore is required",
            }), 400

        if education_score is None:
            return jsonify({
                "success": False,
                "message": "educationScore is required",
            }), 400

        if selected is None:
            return jsonify({
                "success": False,
                "message": "selected is required (boolean: true/false)",
            }), 400

        # Initialize feedback service
        feedback_service = FeedbackService(
            current_app.mongo_db,
            retrain_threshold=current_app.config.get("FEEDBACK_RETRAIN_THRESHOLD", 50),
            min_train_samples=current_app.config.get("FEEDBACK_MIN_TRAIN_SAMPLES", 20),
        )

        # Save feedback and potentially trigger retraining
        success, message, retraining_result = feedback_service.save_feedback(
            resume_id=resume_id,
            job_id=job_id,
            semantic_score=semantic_score,
            experience_score=experience_score,
            education_score=education_score,
            selected=selected,
            recruiter_notes=recruiter_notes,
            user_id=user_id,
        )

        if not success:
            return jsonify({
                "success": False,
                "message": message,
            }), 400

        response = {
            "success": True,
            "message": message,
        }

        # Include retraining info if available
        if retraining_result:
            response["retraining"] = {
                "triggered": retraining_result.get("triggered", False),
                "feedbackCount": retraining_result.get("feedbackCount", 0),
                "reason": retraining_result.get("reason", "unknown"),
            }
            if retraining_result.get("triggered"):
                response["retraining"]["modelPath"] = retraining_result.get("modelPath", "")
                response["retraining"]["sampleCount"] = retraining_result.get("sampleCount", 0)

        return jsonify(response), 201

    except Exception as e:
        logger.exception("Error in save_feedback endpoint")
        return jsonify({
            "success": False,
            "message": f"Internal server error: {str(e)}",
        }), 500


@feedback_bp.route("/feedback", methods=["GET"])
@require_auth
def get_feedback():
    """
    Retrieve feedback records (with optional filtering).
    
    Query parameters:
      - resumeId: Optional filter by resume ID
      - jobId: Optional filter by job ID
      - limit: Maximum records to return (default: 100, max: 1000)
    
    Response:
    {
        "success": true,
        "feedback": [
            {
                "resume_id": "string",
                "job_id": "string",
                "semantic_score": float,
                "experience_score": float,
                "education_score": float,
                "selected": boolean,
                "timestamp": "ISO timestamp",
                "recruiter_notes": "optional string",
                "user_id": "optional string"
            },
            ...
        ],
        "count": integer
    }
    """
    try:
        resume_id = request.args.get("resumeId", "").strip() or None
        job_id = request.args.get("jobId", "").strip() or None
        limit = request.args.get("limit", "100")

        try:
            limit = int(limit)
            limit = min(limit, 1000)  # Cap at 1000 records
            limit = max(limit, 1)     # Minimum 1 record
        except ValueError:
            limit = 100

        feedback_service = FeedbackService(current_app.mongo_db)
        feedback = feedback_service.get_feedback(
            resume_id=resume_id,
            job_id=job_id,
            limit=limit,
        )

        return jsonify({
            "success": True,
            "feedback": feedback,
            "count": len(feedback),
        }), 200

    except Exception as e:
        logger.exception("Error in get_feedback endpoint")
        return jsonify({
            "success": False,
            "message": f"Internal server error: {str(e)}",
        }), 500


@feedback_bp.route("/feedback/stats", methods=["GET"])
@require_auth
def get_feedback_stats():
    """
    Get feedback statistics.
    
    Query parameters:
      - jobId: Optional filter by job ID
    
    Response:
    {
        "success": true,
        "stats": {
            "total_feedback": integer,
            "selected": integer,
            "rejected": integer,
            "selection_rate": float (0-1),
            "avg_semantic_score": float,
            "avg_experience_score": float,
            "avg_education_score": float
        }
    }
    """
    try:
        job_id = request.args.get("jobId", "").strip() or None

        feedback_service = FeedbackService(current_app.mongo_db)
        stats = feedback_service.get_feedback_stats(job_id=job_id)

        if "error" in stats:
            return jsonify({
                "success": False,
                "message": stats["error"],
            }), 500

        return jsonify({
            "success": True,
            "stats": stats,
        }), 200

    except Exception as e:
        logger.exception("Error in get_feedback_stats endpoint")
        return jsonify({
            "success": False,
            "message": f"Internal server error: {str(e)}",
        }), 500


@feedback_bp.route("/feedback/<resume_id>/<job_id>", methods=["DELETE"])
@require_auth
def delete_feedback(resume_id: str, job_id: str):
    """
    Delete feedback for a specific resume-job pair.
    
    Use this when incorrect feedback was submitted and needs to be corrected.
    
    Path parameters:
      - resume_id: Resume identifier
      - job_id: Job identifier
    
    Response (success):
    {
        "success": true,
        "message": "Feedback deleted successfully"
    }
    
    Response (error):
    {
        "success": false,
        "message": "Error message"
    }
    """
    try:
        feedback_service = FeedbackService(current_app.mongo_db)
        success, message = feedback_service.delete_feedback(
            resume_id=resume_id,
            job_id=job_id,
        )

        status_code = 200 if success else 404
        return jsonify({
            "success": success,
            "message": message,
        }), status_code

    except Exception as e:
        logger.exception("Error in delete_feedback endpoint")
        return jsonify({
            "success": False,
            "message": f"Internal server error: {str(e)}",
        }), 500
