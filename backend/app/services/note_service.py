# ============================================================
# Service — Note
# ============================================================

import uuid
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note
from app.models.user import User
from app.repositories.note_repository import NoteRepository
from app.repositories.topic_repository import TopicRepository
from app.schemas.note import NoteCreate, NoteUpdate


class NoteService:
    """Business logic for Note management."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.note_repo = NoteRepository(db)
        self.topic_repo = TopicRepository(db)

    async def _validate_leaf_topic(self, user_id: uuid.UUID, topic_id: uuid.UUID) -> uuid.UUID:
        """
        Validates that the topic exists, belongs to the user, and has 0 children.
        Returns the skill_id of the topic.
        """
        topic = await self.topic_repo.get_by_id(topic_id, user_id)
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found."
            )

        children = await self.topic_repo.get_children(user_id, topic_id)
        if children:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Notes can only be attached to leaf topics."
            )

        return topic.skill_id

    async def create_note(self, current_user: User, data: NoteCreate) -> Note:
        skill_id = await self._validate_leaf_topic(current_user.id, data.topic_id)

        # Convert HttpUrls to strings for JSONB
        urls_str = [str(url) for url in data.urls]

        note = Note(
            user_id=current_user.id,
            skill_id=skill_id,
            topic_id=data.topic_id,
            content=data.content,
            urls=urls_str
        )
        return await self.note_repo.create(note)

    async def get_note(self, current_user: User, note_id: uuid.UUID) -> Note:
        # Include user_id in the query — never fetch then check ownership in Python.
        # This prevents timing-based IDOR where 403 vs 404 reveals note existence.
        note = await self.note_repo.get_by_id_and_user(note_id, current_user.id)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found."
            )
        return note

    async def update_note(self, current_user: User, note_id: uuid.UUID, data: NoteUpdate) -> Note:
        note = await self.get_note(current_user, note_id)
        
        # We allow editing even if the topic is no longer a leaf node.
        
        update_data = data.model_dump(exclude_unset=True)
        
        if "content" in update_data:
            note.content = update_data["content"]
        if "urls" in update_data:
            note.urls = [str(u) for u in update_data["urls"]]

        return await self.note_repo.update(note)

    async def delete_note(self, current_user: User, note_id: uuid.UUID) -> None:
        note = await self.get_note(current_user, note_id)
        await self.note_repo.delete(note)

    async def list_skill_notes(self, current_user: User, skill_id: uuid.UUID, skip: int = 0, limit: int = 50) -> Sequence[Note]:
        return await self.note_repo.get_by_skill(skill_id, current_user.id, skip, limit)

    async def list_topic_notes(self, current_user: User, topic_id: uuid.UUID, skip: int = 0, limit: int = 50) -> Sequence[Note]:
        return await self.note_repo.get_by_topic(topic_id, current_user.id, skip, limit)
