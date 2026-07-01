# ============================================================
# Repository — Note
# ============================================================

import uuid
from typing import Sequence, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note


class NoteRepository:
    """Encapsulates all Note database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, note: Note) -> Note:
        self.db.add(note)
        await self.db.flush()
        await self.db.refresh(note)
        return note

    async def get_by_id(self, note_id: uuid.UUID) -> Optional[Note]:
        result = await self.db.execute(select(Note).where(Note.id == note_id))
        return result.scalar_one_or_none()

    async def get_by_id_and_user(self, note_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Note]:
        """Fetch a note by ID scoped to the owner — prevents IDOR."""
        result = await self.db.execute(
            select(Note).where(Note.id == note_id, Note.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update(self, note: Note) -> Note:
        await self.db.flush()
        await self.db.refresh(note)
        return note

    async def delete(self, note: Note) -> None:
        await self.db.delete(note)
        await self.db.flush()

    async def get_by_skill(self, skill_id: uuid.UUID, user_id: uuid.UUID, skip: int = 0, limit: int = 50) -> Sequence[Note]:
        result = await self.db.execute(
            select(Note)
            .where(Note.skill_id == skill_id, Note.user_id == user_id)
            .order_by(Note.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_topic(self, topic_id: uuid.UUID, user_id: uuid.UUID, skip: int = 0, limit: int = 50) -> Sequence[Note]:
        result = await self.db.execute(
            select(Note)
            .where(Note.topic_id == topic_id, Note.user_id == user_id)
            .order_by(Note.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
