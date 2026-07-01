# ============================================================
# Validators — Skill Domain
# ============================================================

from datetime import datetime
from fastapi import HTTPException, status
from app.utils.date_utils import utc_now


def validate_deadline(deadline: datetime | None) -> None:
    """Ensure deadline is not in the past."""
    if deadline and deadline < utc_now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deadline cannot be in the past."
        )


def validate_pin_limit(current_pinned_count: int, limit: int = 5) -> None:
    """Ensure a user cannot pin more than the allowed limit of skills."""
    if current_pinned_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum pinned skills reached ({limit})."
        )
