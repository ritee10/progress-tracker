# ============================================================
# Schemas — Skill
# ============================================================

import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class SkillCreate(BaseModel):
    """POST /skills request body."""
    title: str = Field(..., min_length=3, max_length=100)
    category: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    difficulty: Optional[str] = Field("beginner", pattern=r"^(beginner|intermediate|advanced)$")
    priority: Optional[str] = Field("medium", pattern=r"^(low|medium|high|critical)$")
    deadline: Optional[datetime] = None
    target_hours: Optional[float] = Field(0.0, ge=0)
    estimated_completion_days: Optional[int] = Field(0, ge=0)
    color: Optional[str] = Field(None, max_length=50)
    icon: Optional[str] = Field(None, max_length=100)


class SkillUpdate(BaseModel):
    """PUT /skills/{id} request body."""
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, max_length=100)
    difficulty: Optional[str] = Field(None, pattern=r"^(beginner|intermediate|advanced)$")
    status: Optional[str] = Field(None, pattern=r"^(not_started|in_progress|completed|on_hold)$")
    priority: Optional[str] = Field(None, pattern=r"^(low|medium|high|critical)$")
    deadline: Optional[datetime] = None
    target_hours: Optional[float] = Field(None, ge=0)
    estimated_completion_days: Optional[int] = Field(None, ge=0)
    color: Optional[str] = Field(None, max_length=50)
    icon: Optional[str] = Field(None, max_length=100)


class SkillResponse(BaseModel):
    """Single skill representation."""
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: str
    target_hours: float
    estimated_completion_days: int
    status: str
    priority: str
    deadline: Optional[datetime] = None
    is_pinned: bool
    color: Optional[str] = None
    icon: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SkillBrief(BaseModel):
    """Minimal skill info for nested references."""
    id: uuid.UUID
    title: str
    category: Optional[str] = None
    status: str

    model_config = {"from_attributes": True}


class SkillStatsResponse(BaseModel):
    """Statistics for user skills."""
    total_skills: int
    active_skills: int
    completed_skills: int
    pinned_skills: int
    overdue_skills: int
