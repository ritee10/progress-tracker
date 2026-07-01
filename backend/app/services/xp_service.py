# ============================================================
# Service — XP
# ============================================================

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.xp import XPRecord


class XPService:
    """Business logic for XP transactions and level calculation."""

    # Level formula: level = floor(sqrt(total_xp) / 5) + 1
    # XP per level increases quadratically, giving diminishing returns.

    def __init__(self, db: AsyncSession):
        self.db = db

    async def award_xp(
        self,
        user_id: uuid.UUID,
        amount: int,
        source_type: str,
        source_id: uuid.UUID | None = None,
        description: str | None = None,
    ) -> XPRecord:
        """Record an XP transaction."""
        record = XPRecord(
            user_id=user_id,
            source_type=source_type,
            source_id=source_id,
            amount=amount,
            description=description,
        )
        self.db.add(record)
        await self.db.flush()
        return record

    async def get_total_xp(self, user_id: uuid.UUID) -> int:
        """Calculate total XP for a user."""
        result = await self.db.execute(
            select(func.coalesce(func.sum(XPRecord.amount), 0)).where(
                XPRecord.user_id == user_id
            )
        )
        return result.scalar_one()

    @staticmethod
    def calculate_level(total_xp: int) -> int:
        """Derive level from total XP using quadratic formula."""
        import math
        return max(1, int(math.floor(math.sqrt(total_xp) / 5)) + 1)

    @staticmethod
    def xp_for_next_level(current_level: int) -> int:
        """XP required to reach the next level."""
        return (current_level * 5) ** 2

    @staticmethod
    def level_progress_percentage(total_xp: int, current_level: int) -> float:
        """Percentage progress toward the next level."""
        current_threshold = ((current_level - 1) * 5) ** 2
        next_threshold = (current_level * 5) ** 2
        range_xp = next_threshold - current_threshold
        if range_xp <= 0:
            return 100.0
        progress = total_xp - current_threshold
        return min(100.0, round((progress / range_xp) * 100, 1))
