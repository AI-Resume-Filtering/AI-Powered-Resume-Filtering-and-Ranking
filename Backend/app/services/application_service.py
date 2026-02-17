import uuid
from datetime import datetime


class ApplicationService:
    def __init__(self, db, pipeline_service=None):
        self.collection = db["applications"]
        self.pipeline = pipeline_service

    def create_application(self, job: dict, candidate: dict, resume_file) -> dict:
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
            "resumeName": resume_file.filename if resume_file else "",
            "resumePdfPath": pipeline_result.get("resumePdfPath"),
            "resumeTextPath": pipeline_result.get("resumeTextPath"),
            "nlpOutputPath": pipeline_result.get("nlpOutputPath"),
            "score": pipeline_result.get("score"),
            "rank": pipeline_result.get("rank"),
            "status": pipeline_result.get("status"),
            "emailSent": pipeline_result.get("emailSent"),
            "createdAt": datetime.utcnow().isoformat(),
        }

        self.collection.insert_one(application)
        return application

    def list_company_resumes(self, company_id: str) -> list:
        return list(self.collection.find({"companyId": company_id}, {"_id": 0}))

    def list_company_history(self, company_id: str) -> list:
        return list(self.collection.find({"companyId": company_id}, {"_id": 0}))

    def get_application(self, application_id: str) -> dict:
        return self.collection.find_one({"applicationId": application_id}, {"_id": 0})
