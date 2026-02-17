from flask import Blueprint, current_app, jsonify, request
import logging

from ..services.company_service import CompanyService

company_bp = Blueprint("company", __name__)
logger = logging.getLogger(__name__)


@company_bp.route("/company/register", methods=["POST"])
def register_company():
    try:
        payload = request.get_json(silent=True) or {}
        required = ["companyName", "registrationNo", "email", "password"]
        
        # Check required fields
        missing = [f for f in required if not payload.get(f)]
        if missing:
            msg = f"Missing required fields: {', '.join(missing)}"
            logger.warning(f"Registration failed: {msg}")
            return jsonify({"success": False, "message": msg}), 400

        service = CompanyService(current_app.mongo_db)
        result = service.register_company(
            company_name=payload["companyName"],
            registration_no=payload["registrationNo"],
            email=payload["email"],
            password=payload["password"],
        )

        status = 200 if result.get("success") else 400
        if not result.get("success"):
            logger.warning(f"Registration failed: {result.get('message')}")
        else:
            logger.info(f"Company registered: {payload['email']}")
        return jsonify(result), status
    except Exception as e:
        logger.exception("Registration error")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


@company_bp.route("/company/login", methods=["POST"])
def login_company():
    try:
        payload = request.get_json(silent=True) or {}
        if not payload.get("email") or not payload.get("password"):
            return jsonify({"success": False, "message": "Email and password required"}), 400

        service = CompanyService(current_app.mongo_db)
        result = service.login_company(payload["email"], payload["password"])
        status = 200 if result.get("success") else 401
        if not result.get("success"):
            logger.warning(f"Login failed for email: {payload['email']}")
        else:
            logger.info(f"Company logged in: {payload['email']}")
        return jsonify(result), status
    except Exception as e:
        logger.exception("Login error")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
