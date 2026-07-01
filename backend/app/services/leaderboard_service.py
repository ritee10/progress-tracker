# ============================================================
# Service — Leaderboard
# ============================================================

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.leaderboard import LeaderboardEntry


class LeaderboardService:
    """Business logic for leaderboard queries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_global_leaderboard(
        self, limit: int = 50, offset: int = 0
    ) -> Sequence[LeaderboardEntry]:
        """Fetch top users by XP."""
        result = await self.db.execute(
            select(LeaderboardEntry)
            .order_by(LeaderboardEntry.global_rank)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_user_rank(self, user_id) -> LeaderboardEntry | None:
        """Fetch a specific user's leaderboard entry."""
        result = await self.db.execute(
            select(LeaderboardEntry).where(
                LeaderboardEntry.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
