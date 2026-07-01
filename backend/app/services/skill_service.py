# ============================================================
# Service — Skill
# ============================================================

import uuid
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill
from app.models.user import User
from app.repositories.skill_repository import SkillRepository
from app.schemas.skill import SkillCreate, SkillUpdate, SkillStatsResponse
from app.utils.pagination import PaginationParams
from app.validators.skill_validator import validate_deadline, validate_pin_limit
from app.utils.date_utils import utc_now


class SkillService:
    """Business logic for Skills."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SkillRepository(db)

    async def create_skill(self, current_user: User, data: SkillCreate) -> Skill:
        """Create a new skill."""
        validate_deadline(data.deadline)
        
        if data.is_pinned:
            pinned_count = await self.repo.count_pinned_skills(current_user.id)
            validate_pin_limit(pinned_count)

        skill = Skill(
            user_id=current_user.id,
            title=data.title,
            description=data.description,
            category=data.category,
            difficulty=data.difficulty,
            priority=data.priority,
            deadline=data.deadline,
            target_hours=data.target_hours,
            estimated_completion_days=data.estimated_completion_days,
            color=data.color,
            icon=data.icon,
            is_pinned=data.is_pinned,
            status="not_started"
        )
        return await self.repo.create(skill)

    async def get_skill(self, current_user: User, skill_id: uuid.UUID) -> Skill:
        """Fetch a specific skill, ensuring ownership."""
        skill = await self.repo.get_by_id(skill_id, current_user.id)
        if not skill:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
        return skill

    async def update_skill(self, current_user: User, skill_id: uuid.UUID, data: SkillUpdate) -> Skill:
        """Update an existing skill."""
        skill = await self.get_skill(current_user, skill_id)
        
        if data.deadline is not None:
            validate_deadline(data.deadline)

        update_data = data.model_dump(exclude_unset=True)
        
        if "is_pinned" in update_data and update_data["is_pinned"] and not skill.is_pinned:
            pinned_count = await self.repo.count_pinned_skills(current_user.id)
            validate_pin_limit(pinned_count)

        for field, value in update_data.items():
            setattr(skill, field, value)

        return await self.repo.update(skill)

    async def delete_skill(self, current_user: User, skill_id: uuid.UUID) -> dict:
        """Soft delete a skill."""
        skill = await self.get_skill(current_user, skill_id)
        await self.repo.soft_delete(skill)
        return {"success": True, "message": "Skill deleted successfully"}

    async def pin_skill(self, current_user: User, skill_id: uuid.UUID) -> Skill:
        """Pin a skill to the top of the list."""
        skill = await self.get_skill(current_user, skill_id)
        if skill.is_pinned:
            return skill
            
        pinned_count = await self.repo.count_pinned_skills(current_user.id)
        validate_pin_limit(pinned_count)
        
        skill.is_pinned = True
        skill = await self.repo.update(skill)

        # Log Activity
        from app.models.activity import ActivityLog
        log = ActivityLog(
            user_id=current_user.id,
            activity_type="SKILL_PINNED",
            entity_id=skill.id,
            metadata_json={"title": skill.title}
        )
        self.db.add(log)
        await self.db.flush()

        return skill

    async def unpin_skill(self, current_user: User, skill_id: uuid.UUID) -> Skill:
        """Unpin a skill."""
        skill = await self.get_skill(current_user, skill_id)
        if not skill.is_pinned:
            return skill
            
        skill.is_pinned = False
        return await self.repo.update(skill)

    async def get_statistics(self, current_user: User) -> SkillStatsResponse:
        """Aggregate skill statistics for the user."""
        total = await self.repo.count_skills(current_user.id)
        active = await self.repo.count_skills(current_user.id, status="in_progress")
        completed = await self.repo.count_skills(current_user.id, status="completed")
        pinned = await self.repo.count_pinned_skills(current_user.id)
        
        # Count overdue skills
        # This requires a slightly different query, let's execute it directly here for stats
        from sqlalchemy import select, func
        stmt = select(func.count(Skill.id)).where(
            Skill.user_id == current_user.id,
            Skill.deleted_at == None, # noqa
            Skill.deadline != None,
            Skill.deadline < utc_now(),
            Skill.status != "completed"
        )
        overdue_result = await self.db.execute(stmt)
        overdue = overdue_result.scalar_one()

        return SkillStatsResponse(
            total_skills=total,
            active_skills=active,
            completed_skills=completed,
            pinned_skills=pinned,
            overdue_skills=overdue
        )
