# ============================================================
# Repository — Topic
# ============================================================

import uuid
from typing import Optional, Sequence

from sqlalchemy import select, update, func, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.topic import Topic
from app.utils.escape import escape_like


class TopicRepository:
    """Data access layer for Topic Tree models."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, topic: Topic) -> Topic:
        self.session.add(topic)
        await self.session.flush()
        await self.session.refresh(topic)
        return topic

    async def get_by_id(self, topic_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Topic]:
        result = await self.session.execute(
            select(Topic).where(
                Topic.id == topic_id,
                Topic.user_id == user_id,
                Topic.deleted_at == None  # noqa
            )
        )
        return result.scalar_one_or_none()

    async def update(self, topic: Topic) -> Topic:
        await self.session.flush()
        await self.session.refresh(topic)
        return topic

    async def get_all_by_user(self, user_id: uuid.UUID) -> Sequence[Topic]:
        """Fetch all non-deleted topics for a user, ordered by depth and index."""
        result = await self.session.execute(
            select(Topic).where(
                Topic.user_id == user_id,
                Topic.deleted_at == None  # noqa
            ).order_by(Topic.depth, Topic.order_index)
        )
        return result.scalars().all()

    async def get_children(self, user_id: uuid.UUID, parent_id: Optional[uuid.UUID]) -> Sequence[Topic]:
        """Fetch direct children of a parent (or roots if parent_id is None)."""
        stmt = select(Topic).where(
            Topic.user_id == user_id,
            Topic.parent_id == parent_id,
            Topic.deleted_at == None  # noqa
        ).order_by(Topic.order_index)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_descendants(self, user_id: uuid.UUID, path_prefix: str) -> Sequence[Topic]:
        """Fetch all descendants using the path prefix (e.g. '/root-id/child-id%')."""
        stmt = select(Topic).where(
            Topic.user_id == user_id,
            Topic.path.like(f"{path_prefix}/%"),
            Topic.deleted_at == None  # noqa
        ).order_by(Topic.depth, Topic.order_index)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_ancestors(self, user_id: uuid.UUID, ancestor_ids: list[str]) -> Sequence[Topic]:
        """Fetch all ancestors given a list of their UUID strings."""
        if not ancestor_ids:
            return []
        
        # Convert strings to UUIDs for the query
        uuids = [uuid.UUID(aid) for aid in ancestor_ids]
        stmt = select(Topic).where(
            Topic.user_id == user_id,
            Topic.id.in_(uuids),
            Topic.deleted_at == None  # noqa
        ).order_by(Topic.depth)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def search(self, user_id: uuid.UUID, query: str) -> Sequence[Topic]:
        """Search topics by title or description."""
        search_term = f"%{escape_like(query)}%"
        stmt = select(Topic).where(
            Topic.user_id == user_id,
            Topic.deleted_at == None,  # noqa
            Topic.is_archived == False,
            or_(
                Topic.title.ilike(search_term),
                Topic.description.ilike(search_term)
            )
        ).order_by(Topic.depth, Topic.order_index)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_max_order_index(self, user_id: uuid.UUID, parent_id: Optional[uuid.UUID]) -> int:
        """Get the highest order index for a set of siblings."""
        stmt = select(func.max(Topic.order_index)).where(
            Topic.user_id == user_id,
            Topic.parent_id == parent_id,
            Topic.deleted_at == None  # noqa
        )
        result = await self.session.execute(stmt)
        max_idx = result.scalar_one_or_none()
        return max_idx if max_idx is not None else -1

    async def batch_update_order(self, user_id: uuid.UUID, ordered_ids: list[uuid.UUID]) -> None:
        """Update order_index for a batch of siblings."""
        # Simple iterative update - for very large sets, a CASE statement or bulk update is better.
        # But since sibling count is usually small, this is safe and framework-agnostic.
        for index, t_id in enumerate(ordered_ids):
            await self.session.execute(
                update(Topic)
                .where(Topic.id == t_id, Topic.user_id == user_id)
                .values(order_index=index)
            )
        await self.session.flush()
