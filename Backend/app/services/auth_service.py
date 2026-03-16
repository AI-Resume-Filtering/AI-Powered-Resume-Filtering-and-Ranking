import jwt
from datetime import datetime, timedelta, timezone

from werkzeug.security import generate_password_hash, check_password_hash

_ALGORITHM = "HS256"
_TOKEN_EXPIRY_HOURS = 24


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, password)


def generate_token(company_id: str, secret_key: str) -> str:
    """Generate a signed JWT for a company session."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": company_id,
        "iat": now,
        "exp": now + timedelta(hours=_TOKEN_EXPIRY_HOURS),
    }
    return jwt.encode(payload, secret_key, algorithm=_ALGORITHM)


def verify_token(token: str, secret_key: str):
    """Verify a JWT and return the company_id (sub), or None if invalid/expired."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=[_ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
