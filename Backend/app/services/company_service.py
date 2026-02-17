import uuid
from datetime import datetime

from .auth_service import hash_password, verify_password


class CompanyService:
    def __init__(self, db):
        self.collection = db["companies"]

    def register_company(self, company_name: str, registration_no: str, email: str, password: str) -> dict:
        existing = self.collection.find_one({"email": email})
        if existing:
            return {"success": False, "message": "Company already exists"}

        company_id = uuid.uuid4().hex
        company = {
            "companyId": company_id,
            "name": company_name,
            "registrationNo": registration_no,
            "email": email,
            "passwordHash": hash_password(password),
            "createdAt": datetime.utcnow().isoformat(),
        }

        self.collection.insert_one(company)
        return {"success": True, "company": self._public_company(company)}

    def login_company(self, email: str, password: str) -> dict:
        company = self.collection.find_one({"email": email})
        if not company:
            return {"success": False, "message": "Invalid email or password"}

        if not verify_password(password, company.get("passwordHash", "")):
            return {"success": False, "message": "Invalid email or password"}

        return {"success": True, "company": self._public_company(company)}

    @staticmethod
    def _public_company(company: dict) -> dict:
        return {
            "companyId": company.get("companyId"),
            "name": company.get("name"),
            "registrationNo": company.get("registrationNo"),
            "email": company.get("email"),
        }
