import uuid
from datetime import date, timedelta
from typing import Optional, List, Dict

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.streak import StreakDay, StreakStats
from app.utils.date_utils import today_utc


class StreakService:
    """Business logic for the event-driven streak engine."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def recordActivity(self, user_id: uuid.UUID, activity_date: Optional[date] = None) -> StreakDay:
        """
        Record a leaf topic completion for a specific date.
        Idempotent: updates existing StreakDay or creates a new one.
        """
        if activity_date is None:
            activity_date = today_utc()

        # Try to fetch existing
        stmt = select(StreakDay).where(
            StreakDay.user_id == user_id, 
            StreakDay.streak_date == activity_date
        )
        existing = (await self.db.execute(stmt)).scalar_one_or_none()

        if existing:
            existing.completed_topics_count += 1
            await self.db.flush()
            return existing

        # Create new streak day using a savepoint to handle concurrent inserts
        # without invalidating the parent transaction
        streak_day = StreakDay(
            user_id=user_id,
            streak_date=activity_date,
            completed_topics_count=1
        )
        self.db.add(streak_day)
        try:
            async with self.db.begin_nested():
                await self.db.flush()
        except IntegrityError:
            # If concurrent insert happened, fetch and update
            existing = (await self.db.execute(stmt)).scalar_one_or_none()
            if existing:
                existing.completed_topics_count += 1
                await self.db.flush()
                return existing

        # It's a new streak day! Perform incremental update of stats
        await self.updateCurrentStreak(user_id, activity_date)
        return streak_day

    async def _get_or_create_stats(self, user_id: uuid.UUID) -> StreakStats:
        stmt = select(StreakStats).where(StreakStats.user_id == user_id)
        stats = (await self.db.execute(stmt)).scalar_one_or_none()
        if not stats:
            stats = StreakStats(user_id=user_id, current_streak=0, longest_streak=0)
            self.db.add(stats)
            await self.db.flush()
        return stats

    async def updateCurrentStreak(self, user_id: uuid.UUID, activity_date: date) -> None:
        """
        Perform incremental update on current and longest streak.
        If gap is detected, triggers deep recalculation.
        """
        stats = await self._get_or_create_stats(user_id)
        
        # If no previous activity, just set to 1
        if not stats.last_activity_date:
            stats.current_streak = 1
            stats.longest_streak = 1
            stats.last_activity_date = activity_date
            await self.db.flush()
            return

        diff = (activity_date - stats.last_activity_date).days

        if diff == 0:
            # Already handled for today
            pass
        elif diff == 1:
            # Consecutive day
            stats.current_streak += 1
            if stats.current_streak > stats.longest_streak:
                stats.longest_streak = stats.current_streak
            stats.last_activity_date = activity_date
        elif diff < 0:
            # Backdated activity (should not happen normally, but deep recalculate if it does)
            stats.current_streak = await self.calculateCurrentStreak(user_id)
            stats.longest_streak = await self.calculateLongestStreak(user_id)
            # Find the true max date
            max_date_stmt = select(StreakDay.streak_date).where(StreakDay.user_id == user_id).order_by(desc(StreakDay.streak_date)).limit(1)
            max_date = (await self.db.execute(max_date_stmt)).scalar()
            stats.last_activity_date = max_date
        else:
            # Gap > 1 day: Streak broken
            stats.current_streak = 1
            stats.last_activity_date = activity_date

        await self.db.flush()

    async def calculateCurrentStreak(self, user_id: uuid.UUID) -> int:
        """
        Deep recalculation engine for Current Streak.
        1. Get all streak dates sorted descending.
        2. Count consecutive days.
        3. Stop at first gap.
        """
        stmt = select(StreakDay.streak_date).where(StreakDay.user_id == user_id).order_by(desc(StreakDay.streak_date))
        dates = (await self.db.execute(stmt)).scalars().all()

        if not dates:
            return 0

        today = today_utc()
        
        # Current streak must anchor to today or yesterday
        first_diff = (today - dates[0]).days
        if first_diff > 1:
            return 0 # Streak broken

        streak_count = 1
        for i in range(1, len(dates)):
            diff = (dates[i-1] - dates[i]).days
            if diff == 1:
                streak_count += 1
            elif diff == 0:
                continue # Multiple entries for same date shouldn't exist, but safe
            else:
                break

        return streak_count

    async def calculateLongestStreak(self, user_id: uuid.UUID) -> int:
        """
        Deep recalculation engine for Longest Streak.
        """
        stmt = select(StreakDay.streak_date).where(StreakDay.user_id == user_id).order_by(StreakDay.streak_date)
        dates = (await self.db.execute(stmt)).scalars().all()

        if not dates:
            return 0

        longest = 1
        current = 1
        for i in range(1, len(dates)):
            diff = (dates[i] - dates[i-1]).days
            if diff == 1:
                current += 1
                if current > longest:
                    longest = current
            elif diff > 1:
                current = 1

        return longest

    async def getHeatmap(self, user_id: uuid.UUID, days: int = 365) -> List[Dict]:
        """
        Returns an array for the GitHub-style heatmap.
        Format: [{"date": "YYYY-MM-DD", "count": X}, ...]
        """
        start_date = today_utc() - timedelta(days=days-1)
        
        stmt = select(StreakDay).where(
            StreakDay.user_id == user_id,
            StreakDay.streak_date >= start_date
        ).order_by(StreakDay.streak_date)
        
        records = (await self.db.execute(stmt)).scalars().all()
        
        return [
            {
                "date": r.streak_date.isoformat(),
                "count": r.completed_topics_count
            }
            for r in records
        ]

    async def getStats(self, user_id: uuid.UUID) -> Dict:
        """
        Return the core streak stats: current, longest, total active days, total completed topics.
        Read-only: does not mutate state.
        """
        stats = await self._get_or_create_stats(user_id)
        
        # Total active days — use COUNT(*) instead of loading all IDs
        from sqlalchemy import func
        count_stmt = select(func.count(StreakDay.id)).where(StreakDay.user_id == user_id)
        active_days = (await self.db.execute(count_stmt)).scalar_one()
        
        # Total completed topics
        sum_stmt = select(func.sum(StreakDay.completed_topics_count)).where(StreakDay.user_id == user_id)
        total_topics = (await self.db.execute(sum_stmt)).scalar() or 0
        
        # Compute current streak without mutating DB state
        current_streak = stats.current_streak
        today = today_utc()
        if stats.last_activity_date and (today - stats.last_activity_date).days > 1:
            current_streak = 0

        return {
            "currentStreak": current_streak,
            "longestStreak": stats.longest_streak,
            "totalActiveDays": active_days,
            "totalCompletedTopics": int(total_topics),
            "lastActivityDate": stats.last_activity_date.isoformat() if stats.last_activity_date else None
        }

    async def getCalendar(self, user_id: uuid.UUID) -> List[str]:
        """
        Return only the dates where a streak occurred.
        """
        stmt = select(StreakDay.streak_date).where(StreakDay.user_id == user_id).order_by(StreakDay.streak_date)
        dates = (await self.db.execute(stmt)).scalars().all()
        return [d.isoformat() for d in dates]

    # Wrappers for legacy code if needed:
    async def get_current_streak(self, user_id: uuid.UUID) -> int:
        stats = await self.getStats(user_id)
        return stats["currentStreak"]
        
    async def get_longest_streak(self, user_id: uuid.UUID) -> int:
        stats = await self.getStats(user_id)
        return stats["longestStreak"]
        
    async def is_active_today(self, user_id: uuid.UUID) -> bool:
        stats = await self.getStats(user_id)
        last_date = stats["lastActivityDate"]
        return last_date == today_utc().isoformat()
