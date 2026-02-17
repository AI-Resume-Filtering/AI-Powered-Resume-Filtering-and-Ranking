import uuid
import os
import sys
from datetime import datetime

# Add project root to path for module imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Resume_Parser.resume_parser import ResumeParser


class JobService:
    def __init__(self, db, storage_service=None):
        self.collection = db["jobs"]
        self.storage = storage_service
        self.parser = ResumeParser()

    def create_job(self, company: dict, job_title: str, jd_file) -> dict:
        if not self.storage:
            raise RuntimeError("Storage service not configured")

        pdf_path = self.storage.save_upload(jd_file, "job_descriptions")
        description_text = self.parser.parse(pdf_path)

        job_id = uuid.uuid4().hex
        job = {
            "jobId": job_id,
            "title": job_title,
            "description": description_text,
            "descriptionPdfPath": pdf_path,
            "companyId": company.get("companyId"),
            "companyName": company.get("name"),
            "companyRegNo": company.get("registrationNo"),
            "companyEmail": company.get("email"),
            "location": "",
            "experience": "",
            "postDate": datetime.utcnow().isoformat(),
        }

        self.collection.insert_one(job)
        return job

    def get_job(self, job_id: str) -> dict:
        return self.collection.find_one({"jobId": job_id})

    def list_jobs(self) -> list:
        return list(self.collection.find({}, {"_id": 0}))

    def list_company_jobs(self, company_id: str) -> list:
        return list(self.collection.find({"companyId": company_id}, {"_id": 0}))

    def delete_job(self, job_id: str) -> bool:
        result = self.collection.delete_one({"jobId": job_id})
        return result.deleted_count > 0
