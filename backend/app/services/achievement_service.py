# ============================================================
# Service — Achievement
# ============================================================

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.achievement import Achievement, UserAchievement


class AchievementService:
    """Business logic for checking and awarding achievements."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_achievements(
        self, user_id: uuid.UUID
    ) -> Sequence[UserAchievement]:
        """Fetch all achievements earned by a user."""
        result = await self.db.execute(
            select(UserAchievement)
            .where(UserAchievement.user_id == user_id)
            .order_by(UserAchievement.created_at.desc())
        )
        return result.scalars().all()

    async def get_recent_achievements(
        self, user_id: uuid.UUID, limit: int = 5
    ) -> Sequence[UserAchievement]:
        """Fetch most recently earned achievements."""
        result = await self.db.execute(
            select(UserAchievement)
            .where(UserAchievement.user_id == user_id)
            .order_by(UserAchievement.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def check_and_award(
        self, user_id: uuid.UUID, criteria_type: str, current_value: int
    ) -> list[Achievement]:
        """
        Check if the user qualifies for any new achievements
        based on a criteria type and current value.

        Returns list of newly awarded achievements.
        """
        # Fetch all matching active achievements
        result = await self.db.execute(
            select(Achievement).where(
                Achievement.criteria_type == criteria_type,
                Achievement.criteria_value <= current_value,
                Achievement.is_active == True,  # noqa
            )
        )
        eligible = result.scalars().all()

        # Check which ones the user hasn't earned yet
        earned_result = await self.db.execute(
            select(UserAchievement.achievement_id).where(
                UserAchievement.user_id == user_id
            )
        )
        already_earned = {row[0] for row in earned_result.all()}

        newly_awarded = []
        for achievement in eligible:
            if achievement.id not in already_earned:
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id,
                )
                self.db.add(user_achievement)
                newly_awarded.append(achievement)

        if newly_awarded:
            await self.db.flush()

        return newly_awarded

    async def get_all_achievements(self) -> Sequence[Achievement]:
        """Fetch the entire achievement catalog."""
        result = await self.db.execute(
            select(Achievement)
            .where(Achievement.is_active == True)  # noqa
            .order_by(Achievement.criteria_value)
        )
        return result.scalars().all()
