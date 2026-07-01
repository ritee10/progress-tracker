# ============================================================
# Repository — Progress
# ============================================================

import uuid
from datetime import date
from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress import Progress
from app.models.topic import Topic
from app.models.skill import Skill
from app.models.topic_completion import TopicCompletion
from app.utils.date_utils import utc_now


class ProgressRepository:
    """Encapsulates all Progress (study session) database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, progress: Progress) -> Progress:
        """Insert a new progress log entry."""
        self.db.add(progress)
        await self.db.flush()
        await self.db.refresh(progress)
        return progress

    async def get_by_user_date_range(
        self,
        user_id: uuid.UUID,
        start_date: date,
        end_date: date,
    ) -> Sequence[Progress]:
        """Fetch progress records within a date range."""
        result = await self.db.execute(
            select(Progress)
            .where(
                Progress.user_id == user_id,
                Progress.session_date >= start_date,
                Progress.session_date <= end_date,
            )
            .order_by(Progress.session_date.desc(), Progress.created_at.desc())
        )
        return result.scalars().all()

    async def get_today_minutes(self, user_id: uuid.UUID, today: date) -> int:
        """Total minutes studied today."""
        result = await self.db.execute(
            select(func.coalesce(func.sum(Progress.duration_minutes), 0)).where(
                Progress.user_id == user_id,
                Progress.session_date == today,
            )
        )
        return result.scalar_one()

    async def get_today_xp(self, user_id: uuid.UUID, today: date) -> int:
        """Total XP earned today."""
        result = await self.db.execute(
            select(func.coalesce(func.sum(Progress.xp_earned), 0)).where(
                Progress.user_id == user_id,
                Progress.session_date == today,
            )
        )
        return result.scalar_one()

    async def get_today_sessions(self, user_id: uuid.UUID, today: date) -> int:
        """Count of sessions today."""
        result = await self.db.execute(
            select(func.count(Progress.id)).where(
                Progress.user_id == user_id,
                Progress.session_date == today,
            )
        )
        return result.scalar_one()

    async def get_total_stats(self, user_id: uuid.UUID) -> dict:
        """Aggregate lifetime stats for a user."""
        result = await self.db.execute(
            select(
                func.coalesce(func.sum(Progress.duration_minutes), 0).label("total_minutes"),
                func.count(Progress.id).label("total_sessions"),
                func.coalesce(func.sum(Progress.xp_earned), 0).label("total_xp"),
                func.round(func.avg(Progress.quality_rating), 1).label("avg_quality"),
                func.round(func.avg(Progress.duration_minutes), 1).label("avg_session_minutes"),
            ).where(Progress.user_id == user_id)
        )
        row = result.one()
        return {
            "total_minutes": row.total_minutes,
            "total_sessions": row.total_sessions,
            "total_xp": row.total_xp,
            "avg_quality": float(row.avg_quality) if row.avg_quality else None,
            "avg_session_minutes": float(row.avg_session_minutes) if row.avg_session_minutes else None,
        }

    async def get_daily_minutes(
        self, user_id: uuid.UUID, start_date: date, end_date: date
    ) -> dict[date, int]:
        """Daily minute totals for a date range (for weekly trend charts)."""
        result = await self.db.execute(
            select(
                Progress.session_date,
                func.coalesce(func.sum(Progress.duration_minutes), 0),
            )
            .where(
                Progress.user_id == user_id,
                Progress.session_date >= start_date,
                Progress.session_date <= end_date,
            )
            .group_by(Progress.session_date)
            .order_by(Progress.session_date)
        )
        return {row[0]: row[1] for row in result.all()}

    async def count_active_days_in_month(
        self, user_id: uuid.UUID, month_start: date, month_end: date
    ) -> int:
        """Count distinct days with activity in a month."""
        result = await self.db.execute(
            select(func.count(func.distinct(Progress.session_date))).where(
                Progress.user_id == user_id,
                Progress.session_date >= month_start,
                Progress.session_date <= month_end,
            )
        )
        return result.scalar_one()

    # ── Phase 7: Progress Tracking Engine Methods ────────────────

    async def get_topic_completion(self, user_id: uuid.UUID, node_id: uuid.UUID) -> Optional[TopicCompletion]:
        """Fetch the completion record for a leaf topic."""
        result = await self.db.execute(
            select(TopicCompletion).where(
                TopicCompletion.user_id == user_id,
                TopicCompletion.node_id == node_id
            )
        )
        return result.scalar_one_or_none()

    async def upsert_topic_completion(self, user_id: uuid.UUID, node_id: uuid.UUID, completed: bool) -> TopicCompletion:
        """Update or insert a completion record."""
        record = await self.get_topic_completion(user_id, node_id)
        if record:
            record.completed = completed
            record.completed_at = utc_now() if completed else None
        else:
            record = TopicCompletion(
                user_id=user_id,
                node_id=node_id,
                completed=completed,
                completed_at=utc_now() if completed else None
            )
            self.db.add(record)
        
        await self.db.flush()
        return record

    async def lock_topic_for_update(self, topic_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Topic]:
        """Fetch a topic with row-level locking to prevent race conditions during recalculation."""
        result = await self.db.execute(
            select(Topic).where(
                Topic.id == topic_id,
                Topic.user_id == user_id,
                Topic.deleted_at == None  # noqa
            ).with_for_update()
        )
        return result.scalar_one_or_none()

    async def lock_skill_for_update(self, skill_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Skill]:
        """Fetch a skill with row-level locking."""
        result = await self.db.execute(
            select(Skill).where(
                Skill.id == skill_id,
                Skill.user_id == user_id,
                Skill.deleted_at == None  # noqa
            ).with_for_update()
        )
        return result.scalar_one_or_none()

    async def get_topic_child_stats(self, parent_id: uuid.UUID, user_id: uuid.UUID) -> tuple[int, int]:
        """Calculate total_children and completed_children based on progress_percent of direct children."""
        # Using progress_percent == 100 to define a 'completed' child node.
        # This aggregates direct children.
        result = await self.db.execute(
            select(
                func.count(Topic.id),
                func.sum(
                    func.case(
                        (Topic.progress_percent >= 100.0, 1), 
                        else_=0
                    )
                )
            ).where(
                Topic.parent_id == parent_id,
                Topic.user_id == user_id,
                Topic.deleted_at == None # noqa
            )
        )
        row = result.one()
        total_children = row[0] or 0
        completed_children = int(row[1]) if row[1] is not None else 0
        return total_children, completed_children

    async def get_skill_leaf_stats(self, skill_id: uuid.UUID, user_id: uuid.UUID) -> tuple[int, int]:
        """Calculate total_leaves and completed_leaves for a given skill."""
        # A leaf node is a node that does not have children.
        # We can identify them by using a LEFT JOIN on self, or using completion table.
        # Since all leaf nodes can have completion status, we can join with topic_completions.
        # Wait, the simplest way is to fetch topics for the skill that are leaves, and sum progress_percent >= 100.
        
        # Subquery to find all parent IDs
        parents_stmt = select(Topic.parent_id).where(
            Topic.skill_id == skill_id, 
            Topic.user_id == user_id,
            Topic.parent_id != None, # noqa
            Topic.deleted_at == None # noqa
        )
        
        # Main query: all topics not in parent IDs
        result = await self.db.execute(
            select(
                func.count(Topic.id),
                func.sum(
                    func.case(
                        (Topic.progress_percent >= 100.0, 1), 
                        else_=0
                    )
                )
            ).where(
                Topic.skill_id == skill_id,
                Topic.user_id == user_id,
                Topic.id.not_in(parents_stmt),
                Topic.deleted_at == None # noqa
            )
        )
        row = result.one()
        total_leaves = row[0] or 0
        completed_leaves = int(row[1]) if row[1] is not None else 0
        return total_leaves, completed_leaves
