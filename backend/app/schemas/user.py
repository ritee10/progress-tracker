# ============================================================
# Schemas — User
# ============================================================

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Shared user fields."""
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=2, max_length=100)


class UserCreate(UserBase):
    """Used internally when creating a user from a registration request."""
    hashed_password: str


class UserUpdate(BaseModel):
    """PATCH /users/me — partial update."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    avatar_url: Optional[str] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)


class UserResponse(BaseModel):
    """Public user representation returned by API."""
    id: uuid.UUID
    email: EmailStr
    username: str
    full_name: str
    avatar_url: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserBrief(BaseModel):
    """Minimal user info for nested references (e.g., leaderboard)."""
    id: uuid.UUID
    username: str
    full_name: str
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}
