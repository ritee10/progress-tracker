# ============================================================
# Repository — User
# ============================================================
# Data access layer for User model.
# All database queries for users are centralised here.
# ============================================================

import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Encapsulates all User database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Fetch a user by primary key (excludes soft-deleted)."""
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.deleted_at == None)  # noqa
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by email address."""
        result = await self.db.execute(
            select(User).where(User.email == email, User.deleted_at == None)  # noqa
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Fetch a user by username."""
        result = await self.db.execute(
            select(User).where(User.username == username, User.deleted_at == None)  # noqa
        )
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        """Insert a new user."""
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user: User) -> User:
        """Persist changes to an existing user."""
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def soft_delete(self, user: User) -> User:
        """Mark a user as deleted without removing the row."""
        from app.utils.date_utils import utc_now
        user.deleted_at = utc_now()
        user.is_active = False
        await self.db.flush()
        return user

    async def count_active(self) -> int:
        """Total count of active, non-deleted users."""
        result = await self.db.execute(
            select(func.count(User.id)).where(
                User.is_active == True, User.deleted_at == None  # noqa
            )
        )
        return result.scalar_one()

    async def email_exists(self, email: str) -> bool:
        """Check if an email is already registered."""
        return (await self.get_by_email(email)) is not None

    async def username_exists(self, username: str) -> bool:
        """Check if a username is already taken."""
        return (await self.get_by_username(username)) is not None
