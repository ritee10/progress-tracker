# ============================================================
# Utility — Standard API Response Wrapper
# ============================================================

from typing import Any, Optional

from pydantic import BaseModel


class APIResponse(BaseModel):
    """
    Standardised API response envelope.

    Every endpoint returns this shape so the frontend
    can parse responses consistently.
    """
    success: bool = True
    message: str = "OK"
    data: Optional[Any] = None
    errors: Optional[list[dict[str, Any]]] = None


def success_response(
    data: Any = None,
    message: str = "OK",
) -> dict[str, Any]:
    """Build a successful API response."""
    return {
        "success": True,
        "message": message,
        "data": data,
        "errors": None,
    }


def error_response(
    message: str = "An error occurred",
    errors: Optional[list[dict[str, Any]]] = None,
    status_code: int = 400,
) -> dict[str, Any]:
    """Build an error API response."""
    return {
        "success": False,
        "message": message,
        "data": None,
        "errors": errors or [],
    }
