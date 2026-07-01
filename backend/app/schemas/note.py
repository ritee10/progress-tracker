# ============================================================
# Schemas — Notes
# ============================================================

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, validator, field_validator


class NoteBase(BaseModel):
    content: str = Field(..., min_length=1, description="Note content. Max 100 words.")
    urls: List[HttpUrl] = Field(default_factory=list, description="External URLs. Max 2.")

    @field_validator('content')
    def validate_word_limit(cls, v):
        word_count = len(v.split())
        if word_count > 100:
            raise ValueError("Note cannot exceed 100 words.")
        return v

    @field_validator('urls')
    def validate_url_limit(cls, v):
        if len(v) > 2:
            raise ValueError("Maximum 2 URLs allowed.")
        return v


class NoteCreate(NoteBase):
    topic_id: uuid.UUID = Field(..., description="UUID of the leaf topic node.")


class NoteUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    urls: Optional[List[HttpUrl]] = None

    @field_validator('content')
    def validate_word_limit(cls, v):
        if v is not None:
            word_count = len(v.split())
            if word_count > 100:
                raise ValueError("Note cannot exceed 100 words.")
        return v

    @field_validator('urls')
    def validate_url_limit(cls, v):
        if v is not None and len(v) > 2:
            raise ValueError("Maximum 2 URLs allowed.")
        return v


class NoteResponse(NoteBase):
    id: uuid.UUID
    user_id: uuid.UUID
    skill_id: uuid.UUID
    topic_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    # Override urls to be strings in response
    urls: List[str]

    model_config = {"from_attributes": True}
