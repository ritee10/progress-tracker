# ============================================================
# Service — Analytics
# ============================================================

import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.progress_repository import ProgressRepository
from app.schemas.dashboard import (
    DashboardResponse,
    RecentAchievement,
    StreakInfo,
    TodaySummary,
    WeeklyTrend,
    XPInfo,
)
from app.schemas.skill import SkillBrief
from app.services.achievement_service import AchievementService
from app.services.streak_service import StreakService
from app.services.xp_service import XPService
from app.repositories.skill_repository import SkillRepository
from app.repositories.task_repository import TaskRepository
from app.utils.date_utils import date_range, start_of_week, end_of_week, today_utc


class AnalyticsService:
    """Assembles the full dashboard payload from multiple services."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.progress_repo = ProgressRepository(db)
        self.skill_repo = SkillRepository(db)
        self.task_repo = TaskRepository(db)
        self.streak_svc = StreakService(db)
        self.xp_svc = XPService(db)
        self.achievement_svc = AchievementService(db)

    async def build_dashboard(self, user_id: uuid.UUID) -> DashboardResponse:
        """Assemble all dashboard widgets into a single response."""
        today = today_utc()
        week_start = start_of_week(today)
        week_end = end_of_week(today)

        # ── Streak ───────────────────────────────────────────
        stats = await self.streak_svc.getStats(user_id)
        active_today = (stats["lastActivityDate"] == today.isoformat())

        streak = StreakInfo(
            current_streak=stats["currentStreak"],
            longest_streak=stats["longestStreak"],
            is_active_today=active_today,
        )

        # ── XP & Level ──────────────────────────────────────
        total_xp = await self.xp_svc.get_total_xp(user_id)
        level = XPService.calculate_level(total_xp)
        xp_info = XPInfo(
            total_xp=total_xp,
            current_level=level,
            xp_to_next_level=XPService.xp_for_next_level(level),
            level_progress_percentage=XPService.level_progress_percentage(total_xp, level),
        )

        # ── Today ────────────────────────────────────────────
        today_minutes = await self.progress_repo.get_today_minutes(user_id, today)
        today_sessions = await self.progress_repo.get_today_sessions(user_id, today)
        today_xp = await self.progress_repo.get_today_xp(user_id, today)
        tasks_completed_today = await self.task_repo.count_completed_today(user_id, today)

        today_summary = TodaySummary(
            study_minutes=today_minutes,
            sessions_count=today_sessions,
            tasks_completed=tasks_completed_today,
            xp_earned=today_xp,
        )

        # ── Weekly Trend ─────────────────────────────────────
        daily_minutes = await self.progress_repo.get_daily_minutes(
            user_id, week_start, week_end
        )
        weekly_trend = [
            WeeklyTrend(
                day=d,
                minutes=daily_minutes.get(d, 0),
            )
            for d in date_range(week_start, week_end)
        ]

        # ── Active Skills ────────────────────────────────────
        skills = await self.skill_repo.get_all_by_user(
            user_id=user_id, offset=0, limit=5, status="in_progress"
        )
        active_skills = [SkillBrief.model_validate(s) for s in skills]

        # ── Recent Achievements ──────────────────────────────
        recent_ua = await self.achievement_svc.get_recent_achievements(user_id, limit=3)
        recent_achievements = []
        for ua in recent_ua:
            if ua.achievement:
                recent_achievements.append(
                    RecentAchievement(
                        id=ua.achievement.id,
                        name=ua.achievement.name,
                        description=ua.achievement.description,
                        icon_url=ua.achievement.icon_url,
                        rarity=ua.achievement.rarity,
                        earned_at=str(ua.created_at),
                    )
                )

        # ── Upcoming Tasks ───────────────────────────────────
        upcoming = await self.task_repo.count_upcoming(user_id, today)

        return DashboardResponse(
            streak=streak,
            xp=xp_info,
            today=today_summary,
            weekly_trend=weekly_trend,
            active_skills=active_skills,
            recent_achievements=recent_achievements,
            upcoming_tasks_count=upcoming,
        )
