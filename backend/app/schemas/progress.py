# ============================================================
# Schemas — Progress
# ============================================================

import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProgressCreate(BaseModel):
    """POST /progress/update request body."""
    skill_id: Optional[uuid.UUID] = None
    activity_type: str = Field(
        "practicing",
        pattern=r"^(reading|watching|coding|practicing|revising|project_work|assessment|note_taking)$"
    )
    duration_minutes: int = Field(..., ge=1, le=720)
    quality_rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = Field(None, max_length=2000)
    session_date: Optional[date] = None  # Defaults to today


class ProgressResponse(BaseModel):
    """Single progress log entry."""
    id: uuid.UUID
    user_id: uuid.UUID
    skill_id: Optional[uuid.UUID] = None
    activity_type: str
    duration_minutes: int
    quality_rating: Optional[int] = None
    notes: Optional[str] = None
    session_date: date
    xp_earned: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ProgressSummary(BaseModel):
    """GET /progress/summary response."""
    total_minutes: int = 0
    total_sessions: int = 0
    total_xp: int = 0
    avg_quality: Optional[float] = None
    avg_session_minutes: Optional[float] = None
    current_streak: int = 0
    longest_streak: int = 0
    skills_in_progress: int = 0
    skills_completed: int = 0
    active_days_this_month: int = 0
    today_minutes: int = 0


# ── Phase 7: Progress Tracking Engine Schemas ────────────────

class ProgressToggleRequest(BaseModel):
    """Request body for toggling completion on a node."""
    node_id: uuid.UUID = Field(..., description="UUID of the leaf topic node.")


class ProgressToggleResponse(BaseModel):
    """Response after toggling completion."""
    completed: bool
    skill_progress: float


class SkillProgressResponse(BaseModel):
    """Full progress report for a skill."""
    skill_id: uuid.UUID
    progress_percent: float
    completed_nodes: int
    total_nodes: int


class NodeProgressResponse(BaseModel):
    """Progress report for a specific topic node."""
    node_id: uuid.UUID
    progress_percent: float
