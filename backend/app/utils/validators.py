# ============================================================
# Utility — Validators
# ============================================================

import re
import uuid
from typing import Any


def is_valid_uuid(value: Any) -> bool:
    """Check if a value is a valid UUID v4 string."""
    try:
        uuid.UUID(str(value), version=4)
        return True
    except (ValueError, AttributeError):
        return False


def is_strong_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength.

    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character

    Returns:
        (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:',.<>?/`~]", password):
        return False, "Password must contain at least one special character"
    return True, ""


def sanitize_string(value: str, max_length: int = 500) -> str:
    """Strip whitespace and truncate to max_length."""
    return value.strip()[:max_length]


def is_valid_username(username: str) -> tuple[bool, str]:
    """
    Validate username format.

    Rules: 3-50 chars, alphanumeric + hyphens + underscores, no leading/trailing hyphens.
    """
    if len(username) < 3 or len(username) > 50:
        return False, "Username must be between 3 and 50 characters"
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$", username):
        return False, "Username must start and end with alphanumeric characters"
    return True, ""
