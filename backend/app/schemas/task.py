# ============================================================
# Schemas — Task
# ============================================================

import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """POST /tasks request body."""
    title: str = Field(..., min_length=3, max_length=300)
    description: Optional[str] = None
    skill_id: Optional[uuid.UUID] = None
    priority: int = Field(3, ge=1, le=5)
    due_date: Optional[date] = None
    estimated_minutes: Optional[int] = Field(None, ge=1, le=720)
    is_recurring: bool = False


class TaskUpdate(BaseModel):
    """PUT /tasks/{id} request body."""
    title: Optional[str] = Field(None, min_length=3, max_length=300)
    description: Optional[str] = None
    skill_id: Optional[uuid.UUID] = None
    status: Optional[str] = Field(
        None,
        pattern=r"^(pending|in_progress|completed|skipped)$"
    )
    priority: Optional[int] = Field(None, ge=1, le=5)
    due_date: Optional[date] = None
    estimated_minutes: Optional[int] = Field(None, ge=1, le=720)
    actual_minutes: Optional[int] = Field(None, ge=0)
    is_recurring: Optional[bool] = None


class TaskResponse(BaseModel):
    """Single task representation."""
    id: uuid.UUID
    user_id: uuid.UUID
    skill_id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    status: str
    priority: int
    due_date: Optional[date] = None
    estimated_minutes: Optional[int] = None
    actual_minutes: Optional[int] = None
    is_recurring: bool
    completed_at: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
