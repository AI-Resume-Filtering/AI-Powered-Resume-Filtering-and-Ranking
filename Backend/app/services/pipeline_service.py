import json
import logging
import os
import sys
from pathlib import Path

# Import AI modules from project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Ai_Scoring.Ai_Scoring.scorer import process_resume_batch
from Ai_Scoring.Ai_Scoring.semantic_matcher import semantic_similarity_score
from Nlp_Engine.Nlp_service import process_resumes
from Resume_Parser.resume_parser import ResumeParser


logger = logging.getLogger(__name__)


class PipelineService:
    def __init__(self, storage_service, email_service, project_root: str, score_threshold: float, db=None):
        self.storage = storage_service
        self.email = email_service
        self.project_root = project_root
        self.score_threshold = score_threshold
        self.parser = ResumeParser()
        self.db = db  # MongoDB client — used to look up company email templates

    # ── Public API ────────────────────────────────────────────────────────────

    def run(self, job: dict, candidate: dict, resume_file) -> dict:
        """Original synchronous entry-point (saves file then delegates to run_from_path)."""
        if not job:
            raise ValueError("Job not found")
        resume_pdf_path = self.storage.save_upload(resume_file, "resumes")
        return self.run_from_path(job, candidate, resume_pdf_path)

    def run_from_path(self, job: dict, candidate: dict, resume_pdf_path: str) -> dict:
        """
        A3: Entry-point used by the async background thread.
        Accepts a pre-saved PDF path so it can run safely outside the request context.
        """
        if not job:
            raise ValueError("Job not found")

        resume_text = self.parser.parse(resume_pdf_path)

        jd_text = job.get("description", "")
        if not jd_text.strip():
            raise ValueError("Job description text is missing")

        resume_txt_path = self.storage.write_text(
            resume_text, f"resume_{candidate['applicationId']}.txt"
        )
        jd_txt_path = self.storage.write_text(
            jd_text, f"job_{job['jobId']}.txt"
        )

        logger.info("Running NLP extraction for application %s", candidate["applicationId"])
        nlp_response = process_resumes(jd_txt_path, [resume_txt_path])
        if not nlp_response.get("success"):
            raise RuntimeError(nlp_response.get("error", "NLP extraction failed"))

        output_path = nlp_response.get("output_path", "")

        # L8: Use pathlib for cross-platform path assembly (handles / and \ equally)
        output_file = (Path(self.project_root) / output_path).resolve()
        logger.info("NLP output file: %s (exists: %s)", output_file, output_file.exists())

        if not output_file.exists():
            raise RuntimeError(f"NLP output file not found: {output_file}")

        with open(output_file, "r", encoding="utf-8") as fh:
            output_data = json.load(fh)

        job_requirements = output_data.get("job_requirements", {})
        semantic_score = semantic_similarity_score(resume_text, jd_text)
        scoring_metadata = {
            "job_requirements": job_requirements,
            "semantic_score": semantic_score,
        }

        logger.info("Running AI scoring for application %s", candidate["applicationId"])
        scored_results = process_resume_batch(output_file.name, scoring_metadata)

        # L11: Empty results is a real error — raise instead of silently scoring 0
        if not scored_results:
            raise RuntimeError(
                "AI scoring returned no results — the resume may not have been parsed correctly. "
                "Ensure the PDF contains selectable text or is not password-protected."
            )

        if "error" in scored_results[0]:
            raise RuntimeError(scored_results[0]["error"])

        result = scored_results[0]
        score = float(result.get("total_score", 0))
        score_details = result.get("details", {})
        status = "Selected" if score >= self.score_threshold else "Rejected"

        email_sent = False
        if status == "Selected" and candidate.get("email"):
            email_sent = self._send_selection_email(job, candidate, score)

        # A7: Clean up temporary text / NLP output files after scoring is done
        self._cleanup_temp_files(resume_txt_path, jd_txt_path, str(output_file))

        return {
            "resumePdfPath": resume_pdf_path,
            "resumeSavedName": os.path.basename(resume_pdf_path),  # L3
            "resumeTextPath": resume_txt_path,
            "nlpOutputPath": output_path,
            "score": score,
            "semanticScore": float(score_details.get("semantic_score", semantic_score)),
            "experienceScore": float(score_details.get("experience_score", 0.0)),
            "educationScore": float(score_details.get("education_score", 0.0)),
            "blendedScore": float(score_details.get("blended_score", 0.0)),
            "scoreSource": score_details.get("score_source", "blended"),
            "status": status,
            "emailSent": email_sent,
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    # ── Template variable substitution ───────────────────────────────────────

    _DEFAULT_SUBJECT = "Congratulations! You have been shortlisted for {jobTitle}"
    _DEFAULT_BODY = (
        "Dear {candidateName},\n\n"
        "We are pleased to inform you that your application for the position of "
        "{jobTitle} at {companyName} has been shortlisted by our AI-powered system.\n\n"
        "Your AI match score: {score}\n\n"
        "Our hiring team will review your profile and reach out to you with the next steps.\n\n"
        "{contactLine}"
        "Best regards,\n"
        "{companyName} Hiring Team"
    )

    def _resolve_template(self, company_id: str) -> dict:
        """Fetch company's custom template; fall back to built-in default."""
        if self.db is not None and company_id:
            try:
                company = self.db["companies"].find_one(
                    {"companyId": company_id}, {"emailTemplate": 1, "_id": 0}
                )
                if company and company.get("emailTemplate"):
                    tpl = company["emailTemplate"]
                    if tpl.get("subject") and tpl.get("body"):
                        return tpl
            except Exception:
                logger.warning("Could not load email template for company %s — using default", company_id)
        return {"subject": self._DEFAULT_SUBJECT, "body": self._DEFAULT_BODY}

    @staticmethod
    def _fill_placeholders(text: str, variables: dict) -> str:
        """Replace {placeholder} tokens in text with actual values."""
        for key, value in variables.items():
            text = text.replace(f"{{{key}}}", str(value))
        return text

    def _send_selection_email(self, job: dict, candidate: dict, score: float) -> bool:
        company_id = job.get("companyId", "")
        contact_email = job.get("companyEmail", "")
        contact_line = f"For any enquiries, contact us at: {contact_email}\n\n" if contact_email else ""

        template = self._resolve_template(company_id)

        variables = {
            "candidateName": candidate.get("fullName", "Candidate"),
            "jobTitle": job.get("title", "the role"),
            "companyName": job.get("companyName", "the company"),
            "score": round(score, 1),
            "contactEmail": contact_email,
            "contactLine": contact_line,
        }

        subject = self._fill_placeholders(template["subject"], variables)
        body = self._fill_placeholders(template["body"], variables)

        try:
            sent = self.email.send_email(candidate["email"], subject, body)
            if sent:
                logger.info(
                    "Selection email sent to %s for job '%s' (score %.1f)",
                    candidate["email"], job.get("title"), score,
                )
            return sent
        except Exception:
            logger.exception("Failed to send selection email to %s", candidate.get("email"))
            return False

    def _cleanup_temp_files(self, *paths: str) -> None:
        """A7: Delete temporary text / NLP output files after the pipeline finishes."""
        for path in paths:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    logger.debug("Cleaned up temp file: %s", path)
                except Exception as exc:
                    logger.warning("Could not clean up temp file %s: %s", path, exc)
