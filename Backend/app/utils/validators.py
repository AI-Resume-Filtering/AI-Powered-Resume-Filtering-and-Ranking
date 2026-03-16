"""
Input validation helpers — enforce length limits and basic format checks
on all data entering from external requests (S5).
"""
import re

_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

# Maximum allowed lengths per field
_MAX_LENS = {
    "fullName": 200,
    "email": 254,
    "phone": 20,
    "degree": 100,
    "branch": 100,
    "companyName": 200,
    "registrationNo": 50,
    "password": 128,
    "jobTitle": 200,
}


def validate_candidate_form(form) -> list:
    """Validate candidate application form fields. Returns list of error strings."""
    errors = []

    full_name = (form.get("fullName") or "").strip()
    if not full_name:
        errors.append("Full name is required")
    elif len(full_name) > _MAX_LENS["fullName"]:
        errors.append(f"Full name must be under {_MAX_LENS['fullName']} characters")

    email = (form.get("email") or "").strip()
    if not email:
        errors.append("Email is required")
    elif len(email) > _MAX_LENS["email"] or not _EMAIL_RE.match(email):
        errors.append("A valid email address is required")

    phone = (form.get("phone") or "").strip()
    if phone and len(phone) > _MAX_LENS["phone"]:
        errors.append(f"Phone must be under {_MAX_LENS['phone']} characters")

    degree = (form.get("degree") or "").strip()
    if degree and len(degree) > _MAX_LENS["degree"]:
        errors.append(f"Degree must be under {_MAX_LENS['degree']} characters")

    branch = (form.get("branch") or "").strip()
    if branch and len(branch) > _MAX_LENS["branch"]:
        errors.append(f"Branch must be under {_MAX_LENS['branch']} characters")

    return errors


def validate_company_registration(payload: dict) -> list:
    """Validate company registration payload. Returns list of error strings."""
    errors = []

    company_name = (payload.get("companyName") or "").strip()
    if not company_name:
        errors.append("Company name is required")
    elif len(company_name) > _MAX_LENS["companyName"]:
        errors.append(f"Company name must be under {_MAX_LENS['companyName']} characters")

    reg_no = (payload.get("registrationNo") or "").strip()
    if not reg_no:
        errors.append("Registration number is required")
    elif len(reg_no) > _MAX_LENS["registrationNo"]:
        errors.append(f"Registration number must be under {_MAX_LENS['registrationNo']} characters")

    email = (payload.get("email") or "").strip()
    if not email:
        errors.append("Email is required")
    elif len(email) > _MAX_LENS["email"] or not _EMAIL_RE.match(email):
        errors.append("A valid email address is required")

    password = payload.get("password") or ""
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    elif len(password) > _MAX_LENS["password"]:
        errors.append("Password is too long (max 128 characters)")

    return errors


def validate_job_post(form) -> list:
    """Validate job posting form. Returns list of error strings."""
    errors = []

    job_title = (form.get("jobTitle") or "").strip()
    if not job_title:
        errors.append("Job title is required")
    elif len(job_title) > _MAX_LENS["jobTitle"]:
        errors.append(f"Job title must be under {_MAX_LENS['jobTitle']} characters")

    return errors
