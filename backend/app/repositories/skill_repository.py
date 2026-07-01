# ============================================================
# Repository — Skill
# ============================================================

import uuid
from typing import Optional, Sequence, Any

from sqlalchemy import select, func, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill
from app.utils.escape import escape_like


class SkillRepository:
    """Data access layer for Skill models."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, skill: Skill) -> Skill:
        self.session.add(skill)
        await self.session.flush()
        await self.session.refresh(skill)
        return skill

    async def get_by_id(self, skill_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Skill]:
        result = await self.session.execute(
            select(Skill).where(
                Skill.id == skill_id,
                Skill.user_id == user_id,
                Skill.deleted_at == None  # noqa
            )
        )
        return result.scalar_one_or_none()

    async def update(self, skill: Skill) -> Skill:
        await self.session.flush()
        await self.session.refresh(skill)
        return skill

    async def soft_delete(self, skill: Skill) -> None:
        from app.utils.date_utils import utc_now
        skill.deleted_at = utc_now()
        await self.session.flush()

    async def list_skills(
        self,
        user_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        difficulty: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        is_pinned: Optional[bool] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Sequence[Skill]:
        """Fetch skills with advanced filtering, search, and sorting."""
        stmt = select(Skill).where(
            Skill.user_id == user_id,
            Skill.deleted_at == None  # noqa
        )

        # Filtering
        if status:
            stmt = stmt.where(Skill.status == status)
        if difficulty:
            stmt = stmt.where(Skill.difficulty == difficulty)
        if priority:
            stmt = stmt.where(Skill.priority == priority)
        if category:
            stmt = stmt.where(Skill.category == category)
        if is_pinned is not None:
            stmt = stmt.where(Skill.is_pinned == is_pinned)
            
        # Search (case-insensitive)
        if search:
            search_term = f"%{escape_like(search)}%"
            stmt = stmt.where(
                or_(
                    Skill.title.ilike(search_term),
                    Skill.description.ilike(search_term)
                )
            )

        # Sorting logic (always pin first if not explicitly searching pinned)
        order_col = getattr(Skill, sort_by, Skill.created_at)
        ordering = desc(order_col) if sort_order == "desc" else asc(order_col)
        
        # Pinned skills should appear first
        stmt = stmt.order_by(desc(Skill.is_pinned), ordering)
        
        # Pagination
        stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_skills(
        self,
        user_id: uuid.UUID,
        status: Optional[str] = None,
        difficulty: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        is_pinned: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> int:
        """Count skills matching the filter criteria for pagination metadata."""
        stmt = select(func.count(Skill.id)).where(
            Skill.user_id == user_id,
            Skill.deleted_at == None  # noqa
        )

        if status:
            stmt = stmt.where(Skill.status == status)
        if difficulty:
            stmt = stmt.where(Skill.difficulty == difficulty)
        if priority:
            stmt = stmt.where(Skill.priority == priority)
        if category:
            stmt = stmt.where(Skill.category == category)
        if is_pinned is not None:
            stmt = stmt.where(Skill.is_pinned == is_pinned)
            
        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Skill.title.ilike(search_term),
                    Skill.description.ilike(search_term)
                )
            )

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def count_pinned_skills(self, user_id: uuid.UUID) -> int:
        """Count how many skills the user currently has pinned."""
        stmt = select(func.count(Skill.id)).where(
            Skill.user_id == user_id,
            Skill.is_pinned == True,
            Skill.deleted_at == None  # noqa
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_upcoming_deadlines(self, user_id: uuid.UUID, limit: int = 10) -> Sequence[Skill]:
        """Fetch next upcoming skill deadlines."""
        from app.utils.date_utils import utc_now
        stmt = select(Skill).where(
            Skill.user_id == user_id,
            Skill.deleted_at == None,  # noqa
            Skill.deadline != None,
            Skill.deadline >= utc_now()
        ).order_by(asc(Skill.deadline)).limit(limit)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_status(self, user_id: uuid.UUID) -> dict[str, int]:
        """Count skills grouped by status for progress summary. Returns a dict of status -> count."""
        result = await self.session.execute(
            select(Skill.status, func.count(Skill.id))
            .where(Skill.user_id == user_id, Skill.deleted_at == None)  # noqa
            .group_by(Skill.status)
        )
        return {row[0]: row[1] for row in result.all()}
