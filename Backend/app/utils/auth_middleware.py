"""
JWT authentication middleware.
Protects company-only endpoints and prevents IDOR attacks.
"""
from functools import wraps

from flask import jsonify, request, current_app

from ..services.auth_service import verify_token


def require_auth(f):
    """
    Decorator that:
    1. Requires a valid Bearer JWT in the Authorization header.
    2. Stores the authenticated company_id in request.auth_company_id.
    3. If the route URL contains a <company_id> parameter, verifies it matches
       the token — preventing one company from accessing another's data (IDOR).
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header[7:]
        company_id = verify_token(token, current_app.config["SECRET_KEY"])
        if not company_id:
            return jsonify({"success": False, "message": "Invalid or expired token. Please log in again."}), 401

        request.auth_company_id = company_id

        # IDOR guard: URL company_id must match the token's company
        url_company_id = kwargs.get("company_id")
        if url_company_id and url_company_id != company_id:
            return jsonify({"success": False, "message": "Access denied"}), 403

        return f(*args, **kwargs)

    return decorated
