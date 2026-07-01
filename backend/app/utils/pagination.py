# ============================================================
# Utility — Pagination
# ============================================================

from typing import Any, Generic, Optional, Sequence, TypeVar

from pydantic import BaseModel, Field

from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query parameters for paginated endpoints."""
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(
        DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE,
        description=f"Items per page (max {MAX_PAGE_SIZE})"
    )

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Standardised paginated response envelope."""
    items: Sequence[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


def paginate(
    items: Sequence[Any],
    total: int,
    page: int,
    page_size: int,
) -> PaginatedResponse:
    """
    Build a PaginatedResponse from a list of items.

    Args:
        items: The items for the current page.
        total: Total count of items across all pages.
        page: Current page number (1-indexed).
        page_size: Items per page.

    Returns:
        PaginatedResponse with computed metadata.
    """
    total_pages = max(1, (total + page_size - 1) // page_size)
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
