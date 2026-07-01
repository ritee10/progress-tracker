# ============================================================
# Service — User
# ============================================================

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse, UserUpdate


class UserService:
    """Business logic for user profile operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def get_profile(self, user: User) -> UserResponse:
        """Return the authenticated user's profile."""
        return UserResponse.model_validate(user)

    async def update_profile(
        self, user: User, data: UserUpdate
    ) -> UserResponse:
        """Update the authenticated user's profile fields."""
        update_data = data.model_dump(exclude_unset=True)

        # Check username uniqueness if changing
        if "username" in update_data and update_data["username"] != user.username:
            if await self.user_repo.username_exists(update_data["username"]):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username is already taken",
                )

        for field, value in update_data.items():
            setattr(user, field, value)

        user = await self.user_repo.update(user)
        return UserResponse.model_validate(user)

    async def deactivate_account(self, user: User) -> dict:
        """Soft-delete the user's account."""
        await self.user_repo.soft_delete(user)
        return {"message": "Account deactivated. You have 30 days to recover."}

    async def get_user_by_id(self, user_id: uuid.UUID) -> UserResponse:
        """Admin: fetch any user by ID."""
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return UserResponse.model_validate(user)
