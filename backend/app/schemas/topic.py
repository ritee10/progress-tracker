# ============================================================
# Schemas — Topic
# ============================================================

import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class TopicCreate(BaseModel):
    """POST /topics request body."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=50)
    skill_id: uuid.UUID = Field(..., description="UUID of the skill this topic belongs to.")


class TopicUpdate(BaseModel):
    """PUT /topics/{id} request body."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=50)


class TopicResponse(BaseModel):
    """Standard Topic representation."""
    id: uuid.UUID
    parent_id: Optional[uuid.UUID]
    title: str
    description: Optional[str]
    icon: Optional[str]
    color: Optional[str]
    order_index: int
    level: int
    path: str
    depth: int
    is_root: bool
    is_pinned: bool
    is_archived: bool
    progress_percent: float = 0.0
    completed: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TopicTreeResponse(TopicResponse):
    """Nested Topic representation for full tree output."""
    children: List["TopicTreeResponse"] = []

    model_config = {"from_attributes": True}


class TopicMoveRequest(BaseModel):
    """POST /topics/{id}/move request body."""
    new_parent_id: Optional[uuid.UUID] = Field(..., description="UUID of new parent, or null to make it a root topic.")


class TopicReorderRequest(BaseModel):
    """POST /topics/reorder request body."""
    parent_id: Optional[uuid.UUID] = Field(None, description="UUID of parent, or null if reordering root topics.")
    topic_ids: List[uuid.UUID] = Field(..., description="Ordered list of topic IDs.")


class TopicSearchResponse(TopicResponse):
    """Topic representation including human readable path for search results."""
    human_readable_path: str

    model_config = {"from_attributes": True}
