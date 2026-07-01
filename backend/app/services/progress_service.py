# ============================================================
# Service — Progress
# ============================================================

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import XP_PER_MINUTE, XP_QUALITY_MULTIPLIER
from app.models.progress import Progress
from app.models.user import User
from app.repositories.progress_repository import ProgressRepository
from app.repositories.topic_repository import TopicRepository
from app.schemas.progress import ProgressCreate, ProgressResponse, ProgressSummary, ProgressToggleResponse
from app.utils.date_utils import today_utc, start_of_month, end_of_month
from app.core.events import events
import uuid
from fastapi import HTTPException, status


class ProgressService:
    """Business logic for progress logging and summaries."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.progress_repo = ProgressRepository(db)

    async def log_progress(
        self, user: User, data: ProgressCreate
    ) -> ProgressResponse:
        """Log a study session and calculate XP."""
        session_date = data.session_date or today_utc()

        # Calculate XP: base (minutes) + quality bonus
        quality = data.quality_rating or 3
        xp = (data.duration_minutes * XP_PER_MINUTE) + (quality * XP_QUALITY_MULTIPLIER)

        progress = Progress(
            user_id=user.id,
            skill_id=data.skill_id,
            activity_type=data.activity_type,
            duration_minutes=data.duration_minutes,
            quality_rating=data.quality_rating,
            notes=data.notes,
            session_date=session_date,
            xp_earned=xp,
        )
        progress = await self.progress_repo.create(progress)
        return ProgressResponse.model_validate(progress)

    async def get_summary(self, user: User) -> ProgressSummary:
        """Build an aggregated progress summary for the dashboard."""
        today = today_utc()
        month_start = start_of_month(today)
        month_end = end_of_month(today)

        # Lifetime stats
        stats = await self.progress_repo.get_total_stats(user.id)

        # Today's stats
        today_minutes = await self.progress_repo.get_today_minutes(user.id, today)

        # Active days this month
        active_days = await self.progress_repo.count_active_days_in_month(
            user.id, month_start, month_end
        )

        # Skill status counts (from skill repository)
        from app.repositories.skill_repository import SkillRepository
        skill_repo = SkillRepository(self.db)
        status_counts = await skill_repo.count_by_status(user.id)

        return ProgressSummary(
            total_minutes=stats["total_minutes"],
            total_sessions=stats["total_sessions"],
            total_xp=stats["total_xp"],
            avg_quality=stats["avg_quality"],
            avg_session_minutes=stats["avg_session_minutes"],
            current_streak=0,   # Populated by streak service
            longest_streak=0,   # Populated by streak service
            skills_in_progress=status_counts.get("in_progress", 0),
            skills_completed=status_counts.get("completed", 0) + status_counts.get("mastered", 0),
            active_days_this_month=active_days,
            today_minutes=today_minutes,
        )


class ProgressCalculationService:
    """
    Core engine for calculating hierarchical progress from leaf topics up to skills.
    Uses bottom-up recalculation with row-level locking.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProgressRepository(db)
        self.topic_repo = TopicRepository(db)

    async def _verify_leaf_node(self, current_user: User, node_id: uuid.UUID) -> None:
        """Ensure the node has no children."""
        children = await self.topic_repo.get_children(current_user.id, node_id)
        if children:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only leaf nodes can be completed"
            )

    async def toggle_completion(self, current_user: User, node_id: uuid.UUID) -> ProgressToggleResponse:
        """Toggle the completion status of a leaf node."""
        await self._verify_leaf_node(current_user, node_id)
        
        record = await self.repo.get_topic_completion(current_user.id, node_id)
        new_status = not record.completed if record else True
        
        return await self._set_completion(current_user, node_id, new_status)

    async def mark_complete(self, current_user: User, node_id: uuid.UUID) -> ProgressToggleResponse:
        """Force mark a leaf node as complete."""
        await self._verify_leaf_node(current_user, node_id)
        return await self._set_completion(current_user, node_id, True)

    async def mark_incomplete(self, current_user: User, node_id: uuid.UUID) -> ProgressToggleResponse:
        """Force mark a leaf node as incomplete."""
        await self._verify_leaf_node(current_user, node_id)
        return await self._set_completion(current_user, node_id, False)

    async def _set_completion(self, current_user: User, node_id: uuid.UUID, completed: bool) -> ProgressToggleResponse:
        """Internal worker to set completion, trigger recalculation, and emit events."""
        # Update completion record
        await self.repo.upsert_topic_completion(current_user.id, node_id, completed)
        
        # Update leaf topic progress (either 0 or 100)
        leaf_topic = await self.repo.lock_topic_for_update(node_id, current_user.id)
        if not leaf_topic:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
            
        leaf_topic.progress_percent = 100.0 if completed else 0.0
        parent_id = leaf_topic.parent_id
        skill_id = leaf_topic.skill_id
        
        await self.db.flush()

        # Trigger Bottom-Up Recalculation
        if parent_id:
            await self.update_ancestors(current_user.id, parent_id)
            
        skill_progress = await self.recalculate_skill(current_user.id, skill_id)

        # Emit event for Streak Engine / XP Engine
        event_name = "leaf_completed_event" if completed else "leaf_incomplete_event"
        await events.emit(event_name, user_id=current_user.id, node_id=node_id)

        # Log Activity for Dashboard
        if completed:
            from app.models.activity import ActivityLog
            from app.utils.date_utils import utc_now
            log = ActivityLog(
                user_id=current_user.id,
                activity_type="TOPIC_COMPLETED",
                entity_id=node_id,
                metadata_json={"title": leaf_topic.title}
            )
            self.db.add(log)

        return ProgressToggleResponse(
            completed=completed,
            skill_progress=skill_progress
        )

    async def update_ancestors(self, user_id: uuid.UUID, parent_id: uuid.UUID) -> None:
        """Recursively walk up the tree and update parents."""
        current_parent_id = parent_id
        
        while current_parent_id is not None:
            # Lock parent
            parent = await self.repo.lock_topic_for_update(current_parent_id, user_id)
            if not parent:
                break
                
            # Calculate stats from direct children
            total_children, completed_children = await self.repo.get_topic_child_stats(current_parent_id, user_id)
            
            parent.total_children = total_children
            parent.completed_children = completed_children
            
            if total_children == 0:
                parent.progress_percent = 0.0
            else:
                # Progress is based on direct children's completion
                parent.progress_percent = round((completed_children / total_children) * 100.0, 2)
                
            await self.db.flush()
            
            # Move up to next ancestor
            current_parent_id = parent.parent_id

    async def recalculate_skill(self, user_id: uuid.UUID, skill_id: uuid.UUID) -> float:
        """Recalculate the total progress of the root skill based on all leaf nodes."""
        skill = await self.repo.lock_skill_for_update(skill_id, user_id)
        if not skill:
            return 0.0
            
        total_leaves, completed_leaves = await self.repo.get_skill_leaf_stats(skill_id, user_id)
        
        skill.total_nodes = total_leaves
        skill.completed_nodes = completed_leaves
        
        if total_leaves == 0:
            skill.progress_percent = 0.0
        else:
            skill.progress_percent = round((completed_leaves / total_leaves) * 100.0, 2)
            
        # Update skill status automatically based on progress
        if skill.progress_percent >= 100.0:
            skill.status = "completed"
        elif skill.progress_percent > 0.0 and skill.status == "not_started":
            skill.status = "in_progress"
            
        from app.utils.date_utils import utc_now
        skill.last_activity_at = utc_now()
            
        await self.db.flush()
        return float(skill.progress_percent)
