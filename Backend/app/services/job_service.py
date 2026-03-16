import uuid
import os
import sys
from datetime import datetime
from typing import Optional

# Add project root to path for module imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class JobService:
    def __init__(self, db, storage_service=None):
        self.collection = db["jobs"]
        self.storage = storage_service
        self._parser = None  # A10: lazy init — only created when actually needed

    @property
    def _resume_parser(self):
        """A10: Instantiate the parser only on first use (avoids import overhead on list/delete calls)."""
        if self._parser is None:
            from Resume_Parser.resume_parser import ResumeParser
            self._parser = ResumeParser()
        return self._parser

    def create_job(self, company: dict, job_title: str, jd_file) -> dict:
        if not self.storage:
            raise RuntimeError("Storage service not configured")

        pdf_path = self.storage.save_upload(jd_file, "job_descriptions")
        description_text = self._resume_parser.parse(pdf_path)

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
            "status": "active",  # A4: job lifecycle field
            "postDate": datetime.utcnow().isoformat(),
        }

        self.collection.insert_one(job)
        return job

    def get_job(self, job_id: str) -> dict:
        return self.collection.find_one({"jobId": job_id})

    def list_jobs(
        self,
        page: int = 1,
        limit: int = 50,
        query: str = "",
        sort: str = "newest",
        posted_within_days: Optional[int] = None,
    ) -> list:
        """A4: Only return active jobs. A6: Paginated + candidate filters."""
        skip = (page - 1) * limit
        filters = {"status": "active"}

        if query:
            filters["$or"] = [
                {"title": {"$regex": query, "$options": "i"}},
                {"companyName": {"$regex": query, "$options": "i"}},
            ]

        if posted_within_days and posted_within_days > 0:
            cutoff = datetime.utcnow().timestamp() - (posted_within_days * 86400)
            cutoff_iso = datetime.utcfromtimestamp(cutoff).isoformat()
            filters["postDate"] = {"$gte": cutoff_iso}

        sort_map = {
            "newest": ("postDate", -1),
            "oldest": ("postDate", 1),
            "company": ("companyName", 1),
        }
        sort_field, sort_order = sort_map.get(sort, sort_map["newest"])

        return list(
            self.collection.find(
                filters,
                {"_id": 0}
            ).sort(sort_field, sort_order).skip(skip).limit(limit)
        )

    def list_company_jobs(self, company_id: str, page: int = 1, limit: int = 50) -> list:
        """A6: Paginated."""
        skip = (page - 1) * limit
        return list(
            self.collection.find(
                {"companyId": company_id},
                {"_id": 0}
            ).sort("postDate", -1).skip(skip).limit(limit)
        )

    def delete_job(self, job_id: str) -> bool:
        result = self.collection.delete_one({"jobId": job_id})
        if result.deleted_count > 0:
            # L2: delete all applications for this job so they don't become orphans
            db = self.collection.database
            db["applications"].delete_many({"jobId": job_id})
            return True
        return False
