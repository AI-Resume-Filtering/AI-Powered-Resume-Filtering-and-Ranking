"""
Feedback Service - Handles collection and management of recruiter feedback for self-learning system.

Responsibilities:
  • Validate and save recruiter decisions (selected/rejected)
  • Calculate feedback statistics
  • Trigger model retraining when thresholds are met
  • Manage feedback collection in MongoDB
"""

import logging
import os
import sys
import importlib
from datetime import datetime
from typing import Optional, Dict, Tuple

# Ensure project root is importable when backend is run directly.
<<<<<<< HEAD
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
=======
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
>>>>>>> 6b2582cb0fb6189a0f8327284cf4d76c3fdcbca1
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def _load_retrainer():
    """Load retraining function lazily so missing AI module does not break backend startup."""
    try:
        module = importlib.import_module("Ai_Scoring.Ai_Scoring.model_trainer")
        return getattr(module, "maybe_retrain_model", None)
    except Exception:
        return None

logger = logging.getLogger(__name__)


class FeedbackService:
    """Service for managing candidate ranking feedback and model retraining."""

    def __init__(self, db, retrain_threshold: int = 50, min_train_samples: int = 20):
        """
        Initialize FeedbackService.
        
        Args:
            db: MongoDB database connection
            retrain_threshold: Trigger retraining every N feedback entries
            min_train_samples: Minimum samples required to train model
        """
        self.db = db
        self.retrain_threshold = retrain_threshold
        self.min_train_samples = min_train_samples

    def save_feedback(
        self,
        resume_id: str,
        job_id: str,
        semantic_score: float,
        experience_score: float,
        education_score: float,
        selected: bool,
        recruiter_notes: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[Dict]]:
        """
        Save recruiter feedback for a candidate-job pair.
        
        NOTE: All scores should be normalized to [0, 100] or [0, 1].
        This function normalizes semantic_score to [0, 1] if needed.
        
        Args:
            resume_id: Unique identifier for the resume
            job_id: Unique identifier for the job
            semantic_score: Semantic similarity score (0-1 or 0-100)
            experience_score: Experience match score (0-100)
            education_score: Education match score (0-100)
            selected: Whether recruiter selected the candidate
            recruiter_notes: Optional notes from recruiter
            user_id: Optional ID of recruiter providing feedback
        
        Returns:
            Tuple[success: bool, message: str, retraining_result: Optional[Dict]]
        """
        try:
            # Validate required fields
            if not resume_id or not job_id:
                return False, "resume_id and job_id are required", None

            # Normalize and validate scores
            try:
                semantic_score = float(semantic_score)
                experience_score = float(experience_score)
                education_score = float(education_score)
            except (ValueError, TypeError):
                return False, "Scores must be numeric values", None

            # Normalize semantic_score to [0, 1] if it's in [0, 100]
            if semantic_score > 1.0:
                semantic_score = semantic_score / 100.0

            # Clamp all scores to valid ranges
            semantic_score = max(0.0, min(1.0, semantic_score))
            experience_score = max(0.0, min(100.0, experience_score))
            education_score = max(0.0, min(100.0, education_score))

            # Validate selected boolean
            if isinstance(selected, str):
                selected = selected.strip().lower() in {"1", "true", "yes", "selected"}
            elif not isinstance(selected, bool):
                selected = bool(selected)

            # Create feedback document
            feedback_doc = {
                "resume_id": str(resume_id),
                "job_id": str(job_id),
                "semantic_score": semantic_score,
                "experience_score": experience_score,
                "education_score": education_score,
                "selected": selected,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Add optional fields
            if recruiter_notes:
                feedback_doc["recruiter_notes"] = str(recruiter_notes).strip()
            if user_id:
                feedback_doc["user_id"] = str(user_id)

            # Insert into database
            result = self.db["feedback"].insert_one(feedback_doc)
            logger.info(
                "Feedback saved: resume_id=%s, job_id=%s, selected=%s",
                resume_id, job_id, selected
            )

            # Check if we should trigger retraining
            retraining_result = None
            maybe_retrain_model = _load_retrainer()
            if maybe_retrain_model is not None:
                retraining_result = maybe_retrain_model(
                    self.db,
                    retrain_threshold=self.retrain_threshold,
                    min_samples=self.min_train_samples,
                )
                if retraining_result.get("triggered"):
                    logger.info(
                        "Model retraining triggered after feedback entry %s",
                        result.inserted_id
                    )

            return True, "Feedback saved successfully", retraining_result

        except Exception as e:
            logger.exception("Error saving feedback")
            return False, f"Error saving feedback: {str(e)}", None

    def get_feedback_stats(self, job_id: Optional[str] = None) -> Dict:
        """
        Get statistics about collected feedback.
        
        Args:
            job_id: Optional job ID to filter feedback by job
        
        Returns:
            Dictionary with feedback statistics
        """
        try:
            match_stage = {}
            if job_id:
                match_stage = {"$match": {"job_id": str(job_id)}}

            pipeline = []
            if match_stage:
                pipeline.append(match_stage)

            pipeline.extend([
                {
                    "$group": {
                        "_id": None,
                        "total_feedback": {"$sum": 1},
                        "selected_count": {
                            "$sum": {"$cond": [{"$eq": ["$selected", True]}, 1, 0]}
                        },
                        "rejected_count": {
                            "$sum": {"$cond": [{"$eq": ["$selected", False]}, 1, 0]}
                        },
                        "avg_semantic_score": {"$avg": "$semantic_score"},
                        "avg_experience_score": {"$avg": "$experience_score"},
                        "avg_education_score": {"$avg": "$education_score"},
                    }
                }
            ])

            result = list(self.db["feedback"].aggregate(pipeline))
            if result:
                stats = result[0]
                stats.pop("_id", None)
                return {
                    "total_feedback": stats.get("total_feedback", 0),
                    "selected": stats.get("selected_count", 0),
                    "rejected": stats.get("rejected_count", 0),
                    "selection_rate": (
                        stats.get("selected_count", 0) /
                        max(1, stats.get("total_feedback", 1))
                    ),
                    "avg_semantic_score": round(
                        stats.get("avg_semantic_score", 0), 4
                    ),
                    "avg_experience_score": round(
                        stats.get("avg_experience_score", 0), 4
                    ),
                    "avg_education_score": round(
                        stats.get("avg_education_score", 0), 4
                    ),
                }
            return {
                "total_feedback": 0,
                "selected": 0,
                "rejected": 0,
                "selection_rate": 0.0,
                "avg_semantic_score": 0.0,
                "avg_experience_score": 0.0,
                "avg_education_score": 0.0,
            }

        except Exception as e:
            logger.exception("Error retrieving feedback statistics")
            return {"error": str(e)}

    def get_feedback(
        self,
        resume_id: Optional[str] = None,
        job_id: Optional[str] = None,
        limit: int = 100,
    ) -> list:
        """
        Retrieve feedback records.
        
        Args:
            resume_id: Optional resume ID to filter by
            job_id: Optional job ID to filter by
            limit: Maximum number of records to return
        
        Returns:
            List of feedback documents
        """
        try:
            query = {}
            if resume_id:
                query["resume_id"] = str(resume_id)
            if job_id:
                query["job_id"] = str(job_id)

            feedback = list(
                self.db["feedback"]
                .find(query)
                .sort("timestamp", -1)
                .limit(limit)
            )

            # Remove MongoDB _id for cleaner API responses
            for doc in feedback:
                doc.pop("_id", None)

            return feedback

        except Exception as e:
            logger.exception("Error retrieving feedback")
            return []

    def delete_feedback(self, resume_id: str, job_id: str) -> Tuple[bool, str]:
        """
        Delete feedback for a specific resume-job pair (for corrections).
        
        Args:
            resume_id: Resume identifier
            job_id: Job identifier
        
        Returns:
            Tuple[success: bool, message: str]
        """
        try:
            result = self.db["feedback"].delete_one({
                "resume_id": str(resume_id),
                "job_id": str(job_id),
            })

            if result.deleted_count > 0:
                logger.info(
                    "Deleted feedback for resume=%s, job=%s",
                    resume_id, job_id
                )
                return True, "Feedback deleted successfully"
            else:
                return False, "Feedback not found"

        except Exception as e:
            logger.exception("Error deleting feedback")
            return False, f"Error deleting feedback: {str(e)}"
