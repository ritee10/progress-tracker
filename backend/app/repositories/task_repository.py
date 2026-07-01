# ============================================================
# Repository — Task
# ============================================================

import uuid
from datetime import date
from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task


class TaskRepository:
    """Encapsulates all Task database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self, task_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Task]:
        """Fetch a single task belonging to a user."""
        result = await self.db.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_all_by_user(
        self,
        user_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        skill_id: Optional[uuid.UUID] = None,
    ) -> Sequence[Task]:
        """Fetch tasks for a user with optional filters."""
        query = select(Task).where(Task.user_id == user_id)

        if status:
            query = query.where(Task.status == status)
        if skill_id:
            query = query.where(Task.skill_id == skill_id)

        query = query.order_by(
            Task.priority, Task.due_date.asc().nullslast(), Task.created_at.desc()
        ).offset(offset).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def count_by_user(
        self,
        user_id: uuid.UUID,
        status: Optional[str] = None,
        skill_id: Optional[uuid.UUID] = None,
    ) -> int:
        """Count tasks for pagination."""
        query = select(func.count(Task.id)).where(Task.user_id == user_id)
        if status:
            query = query.where(Task.status == status)
        if skill_id:
            query = query.where(Task.skill_id == skill_id)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def create(self, task: Task) -> Task:
        """Insert a new task."""
        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def update(self, task: Task) -> Task:
        """Persist changes to an existing task."""
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def delete(self, task: Task) -> None:
        """Hard-delete a task (tasks are not soft-deleted)."""
        await self.db.delete(task)
        await self.db.flush()

    async def count_upcoming(self, user_id: uuid.UUID, today: date) -> int:
        """Count incomplete tasks due today or in the future."""
        result = await self.db.execute(
            select(func.count(Task.id)).where(
                Task.user_id == user_id,
                Task.status.in_(["pending", "in_progress"]),
                Task.due_date >= today,
            )
        )
        return result.scalar_one()

    async def count_completed_today(
        self, user_id: uuid.UUID, today: date
    ) -> int:
        """Count tasks completed today."""
        result = await self.db.execute(
            select(func.count(Task.id)).where(
                Task.user_id == user_id,
                Task.completed_at == today,
            )
        )
        return result.scalar_one()
