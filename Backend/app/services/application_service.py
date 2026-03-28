import uuid
from datetime import datetime


class ApplicationService:
    def __init__(self, db, pipeline_service=None):
        self.collection = db["applications"]
        self.pipeline = pipeline_service

    def create_application(self, job: dict, candidate: dict, resume_file) -> dict:
        # L1: Prevent duplicate applications (same email + same job)
        existing = self.collection.find_one({
            "jobId": job.get("jobId"),
            "email": candidate.get("email"),
            "status": {"$in": ["processing", "Selected", "Rejected"]},
        })
        if existing:
            raise ValueError("You have already applied for this position.")

        application_id = uuid.uuid4().hex
        candidate["applicationId"] = application_id

        if not self.pipeline:
            raise RuntimeError("Pipeline service not configured")

        pipeline_result = self.pipeline.run(job, candidate, resume_file)

        application = {
            "applicationId": application_id,
            "jobId": job.get("jobId"),
            "jobTitle": job.get("title"),
            "companyId": job.get("companyId"),
            "companyRegNo": job.get("companyRegNo"),
            "candidateName": candidate.get("fullName"),
            "email": candidate.get("email"),
            "phone": candidate.get("phone"),
            "degree": candidate.get("degree"),
            "branch": candidate.get("branch"),
            # L3: Store the saved filename (basename of the actual path on disk)
            "resumeName": pipeline_result.get("resumeSavedName", resume_file.filename or ""),
            "resumePdfPath": pipeline_result.get("resumePdfPath"),
            "resumeTextPath": pipeline_result.get("resumeTextPath"),
            "nlpOutputPath": pipeline_result.get("nlpOutputPath"),
            "score": pipeline_result.get("score"),
            "rank": None,  # L4: rank is always computed dynamically at read time
            "status": pipeline_result.get("status"),
            "emailSent": pipeline_result.get("emailSent"),
            "createdAt": datetime.utcnow().isoformat(),
        }

        self.collection.insert_one(application)
        return application

    def list_company_resumes(self, company_id: str, page: int = 1, limit: int = 100) -> list:
        """A5/A6: Resume view — projection focused on resume fields, with pagination."""
        skip = (page - 1) * limit
        return list(
            self.collection.find(
                {"companyId": company_id},
                {
                    "_id": 0,
                    "applicationId": 1, "jobId": 1, "jobTitle": 1,
                    "candidateName": 1, "email": 1, "resumeName": 1,
                    "status": 1, "score": 1, "resumePdfPath": 1,
                }
            ).sort("createdAt", -1).skip(skip).limit(limit)
        )

    def list_company_history(self, company_id: str, page: int = 1, limit: int = 100) -> list:
        """A5/A6: History view — projection focused on timeline fields, newest first."""
        skip = (page - 1) * limit
        return list(
            self.collection.find(
                {"companyId": company_id},
                {
                    "_id": 0,
                    "applicationId": 1, "jobId": 1, "jobTitle": 1,
                    "candidateName": 1, "email": 1,
                    "status": 1, "score": 1, "createdAt": 1,
                }
            ).sort("createdAt", -1).skip(skip).limit(limit)
        )

    def get_application(self, application_id: str) -> dict:
        return self.collection.find_one({"applicationId": application_id}, {"_id": 0})
