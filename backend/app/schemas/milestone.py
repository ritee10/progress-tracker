# ============================================================
# Schemas — Milestone
# ============================================================

import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class MilestoneCreate(BaseModel):
    """POST /milestones request body."""
    skill_id: uuid.UUID
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    milestone_order: int = Field(0, ge=0)
    target_value: Optional[int] = Field(None, ge=1)
    unit: Optional[str] = Field(None, max_length=50)
    target_date: Optional[date] = None


class MilestoneUpdate(BaseModel):
    """PUT /milestones/{id} request body."""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    milestone_order: Optional[int] = Field(None, ge=0)
    target_value: Optional[int] = Field(None, ge=1)
    current_value: Optional[int] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    target_date: Optional[date] = None
    is_completed: Optional[bool] = None


class MilestoneResponse(BaseModel):
    """Single milestone representation."""
    id: uuid.UUID
    skill_id: uuid.UUID
    title: str
    description: Optional[str] = None
    milestone_order: int
    target_value: Optional[int] = None
    current_value: int
    unit: Optional[str] = None
    target_date: Optional[date] = None
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
