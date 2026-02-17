import json
import logging
import os
import sys
from pathlib import Path

# Add project root to path for module imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Ai_Scoring.Ai_Scoring.scorer import process_resume_batch
from Nlp_Engine.Nlp_service import process_resumes
from Resume_Parser.resume_parser import ResumeParser


logger = logging.getLogger(__name__)


class PipelineService:
    def __init__(self, storage_service, email_service, project_root: str, score_threshold: float):
        self.storage = storage_service
        self.email = email_service
        self.project_root = project_root
        self.score_threshold = score_threshold
        self.parser = ResumeParser()

    def run(self, job: dict, candidate: dict, resume_file) -> dict:
        if not job:
            raise ValueError("Job not found")

        resume_pdf_path = self.storage.save_upload(resume_file, "resumes")
        resume_text = self.parser.parse(resume_pdf_path)

        jd_text = job.get("description", "")
        if not jd_text.strip():
            raise ValueError("Job description text is missing")

        resume_txt_path = self.storage.write_text(resume_text, f"resume_{candidate['applicationId']}.txt")
        jd_txt_path = self.storage.write_text(jd_text, f"job_{job['jobId']}.txt")

        logger.info("Running NLP extraction")
        nlp_response = process_resumes(jd_txt_path, [resume_txt_path])
        if not nlp_response.get("success"):
            raise RuntimeError(nlp_response.get("error", "NLP extraction failed"))

        output_path = nlp_response.get("output_path", "")
        output_file = os.path.join(self.project_root, output_path)
        output_file = os.path.normpath(output_file)

        logger.info(f"Looking for NLP output at: {output_file}")
        logger.info(f"File exists: {os.path.exists(output_file)}")
        
        if not os.path.exists(output_file):
            raise RuntimeError(f"NLP output file not found: {output_file}")

        with open(output_file, "r", encoding="utf-8") as file_obj:
            output_data = json.load(file_obj)

        job_requirements = output_data.get("job_requirements", {})
        scoring_metadata = {"job_requirements": job_requirements}

        logger.info("Running AI scoring")
        scored_results = process_resume_batch(Path(output_file).name, scoring_metadata)

        if scored_results and "error" in scored_results[0]:
            raise RuntimeError(scored_results[0].get("error"))

        result = scored_results[0] if scored_results else {}
        score = float(result.get("total_score", 0))
        status = "Selected" if score >= self.score_threshold else "Rejected"

        email_sent = False
        if status == "Selected" and candidate.get("email"):
            subject = f"Shortlisted: {job.get('title', 'Your application')}"
            contact_email = job.get("companyEmail")
            contact_line = f"Contact: {contact_email}\n" if contact_email else ""
            body = (
                f"Hello {candidate.get('fullName')},\n\n"
                f"Great news — your application for {job.get('title')} at {job.get('companyName')} "
                "has been shortlisted.\n\n"
                "What happens next:\n"
                "- Our hiring team will review your profile in detail\n"
                "- If your profile matches our current needs, we will email you the next steps (assessment/interview)\n\n"
                "Your application summary:\n"
                f"- Position: {job.get('title')}\n"
                f"- Company: {job.get('companyName')}\n"
                f"- Score: {score}\n\n"
                f"Thank you for your interest in {job.get('companyName')}.\n"
                "Please keep an eye on your inbox — we will be in touch soon.\n\n"
                f"{contact_line}\n"
                "Best regards,\n"
                f"{job.get('companyName', 'Hiring Team')} Hiring Team"
            )
            self.email.send_email(candidate["email"], subject, body)
            email_sent = True

        return {
            "resumePdfPath": resume_pdf_path,
            "resumeTextPath": resume_txt_path,
            "nlpOutputPath": output_path,
            "score": score,
            "rank": result.get("rank"),
            "status": status,
            "emailSent": email_sent,
        }
