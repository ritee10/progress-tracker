# ============================================================
# Security Utilities — JWT
# ============================================================

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()


def create_access_token(
    subject: str,
    extra_claims: Optional[dict[str, Any]] = None,
) -> str:
    """Create a short-lived JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    subject: str,
    extra_claims: Optional[dict[str, Any]] = None,
) -> str:
    """Create a long-lived JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh",
    }
    if extra_claims:
        payload.update(extra_claims)
        
    return jwt.encode(payload, settings.JWT_REFRESH_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str, is_refresh: bool = False) -> dict[str, Any]:
    """
    Decode and validate a JWT token.
    Uses JWT_REFRESH_SECRET if is_refresh=True, else JWT_SECRET_KEY.
    """
    secret = settings.JWT_REFRESH_SECRET if is_refresh else settings.JWT_SECRET_KEY
    return jwt.decode(
        token,
        secret,
        algorithms=[settings.JWT_ALGORITHM],
    )


def verify_token(token: str, is_refresh: bool = False) -> tuple[bool, Optional[dict[str, Any]]]:
    """Verify if a token is valid, returning status and payload."""
    try:
        payload = decode_token(token, is_refresh=is_refresh)
        return True, payload
    except JWTError:
        return False, None
