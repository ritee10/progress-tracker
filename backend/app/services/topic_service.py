# ============================================================
# Service — Topic
# ============================================================

import uuid
from typing import List, Sequence, Optional, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.topic import Topic
from app.models.user import User
from app.repositories.topic_repository import TopicRepository
from app.schemas.topic import TopicCreate, TopicUpdate, TopicTreeResponse
from app.utils.date_utils import utc_now


class TopicService:
    """Business logic for unlimited depth Topic Tree."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TopicRepository(db)

    async def create_root_topic(self, current_user: User, data: TopicCreate) -> Topic:
        """Create a new root level topic."""
        return await self._create_topic(current_user, data, parent=None)

    async def create_child_topic(self, current_user: User, parent_id: uuid.UUID, data: TopicCreate) -> Topic:
        """Create a new child topic under a specific parent."""
        parent = await self.get_topic(current_user, parent_id)
        return await self._create_topic(current_user, data, parent)

    async def _create_topic(self, current_user: User, data: TopicCreate, parent: Optional[Topic]) -> Topic:
        topic_id = uuid.uuid4()
        
        # Calculate level, depth, and path
        if parent:
            level = parent.level + 1
            depth = parent.depth + 1
            path = f"{parent.path}/{topic_id}"
            parent_id = parent.id
            is_root = False
        else:
            level = 0
            depth = 0
            path = f"/{topic_id}"
            parent_id = None
            is_root = True

        # Append to end of siblings
        max_idx = await self.repo.get_max_order_index(current_user.id, parent_id)
        
        topic = Topic(
            id=topic_id,
            user_id=current_user.id,
            parent_id=parent_id,
            title=data.title,
            description=data.description,
            icon=data.icon,
            color=data.color,
            order_index=max_idx + 1,
            level=level,
            path=path,
            depth=depth,
            is_root=is_root,
        )
        return await self.repo.create(topic)

    async def get_topic(self, current_user: User, topic_id: uuid.UUID) -> Topic:
        """Fetch a specific topic."""
        topic = await self.repo.get_by_id(topic_id, current_user.id)
        if not topic:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
        return topic

    async def update_topic(self, current_user: User, topic_id: uuid.UUID, data: TopicUpdate) -> Topic:
        """Update metadata for a topic."""
        topic = await self.get_topic(current_user, topic_id)
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(topic, field, value)

        return await self.repo.update(topic)

    async def soft_delete_topic(self, current_user: User, topic_id: uuid.UUID) -> None:
        """Soft delete a topic and recursively delete all its descendants."""
        topic = await self.get_topic(current_user, topic_id)
        descendants = await self.repo.get_descendants(current_user.id, topic.path)
        
        now = utc_now()
        topic.deleted_at = now
        for desc in descendants:
            desc.deleted_at = now
            
        await self.db.flush()

    async def restore_topic(self, current_user: User, topic_id: uuid.UUID) -> None:
        """Restore a topic and its descendants. Note: Repo usually filters out deleted. We need direct query here."""
        from sqlalchemy import select
        # Custom query to find the deleted topic
        result = await self.db.execute(
            select(Topic).where(Topic.id == topic_id, Topic.user_id == current_user.id)
        )
        topic = result.scalar_one_or_none()
        if not topic or not topic.deleted_at:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deleted topic not found")

        # Also get deleted descendants
        desc_result = await self.db.execute(
            select(Topic).where(
                Topic.user_id == current_user.id,
                Topic.path.like(f"{topic.path}/%")
            )
        )
        descendants = desc_result.scalars().all()

        topic.deleted_at = None
        for desc in descendants:
            desc.deleted_at = None
            
        await self.db.flush()

    async def get_tree(self, current_user: User) -> List[TopicTreeResponse]:
        """Fetch the entire topic tree for a user."""
        all_topics = await self.repo.get_all_by_user(current_user.id)
        return self._build_tree(all_topics)

    async def get_subtree(self, current_user: User, topic_id: uuid.UUID) -> TopicTreeResponse:
        """Fetch a specific subtree starting at the given topic."""
        root = await self.get_topic(current_user, topic_id)
        descendants = await self.repo.get_descendants(current_user.id, root.path)
        
        all_nodes = [root] + list(descendants)
        tree = self._build_tree(all_nodes, root_id=root.id)
        return tree[0] if tree else None

    def _build_tree(self, topics: Sequence[Topic], root_id: Optional[uuid.UUID] = None) -> List[TopicTreeResponse]:
        """Convert a flat list of topics into a nested TreeResponse list."""
        lookup: Dict[uuid.UUID, dict] = {}
        roots = []

        # Convert to dicts representing TopicTreeResponse
        for t in topics:
            lookup[t.id] = {
                "id": t.id,
                "parent_id": t.parent_id,
                "title": t.title,
                "description": t.description,
                "icon": t.icon,
                "color": t.color,
                "order_index": t.order_index,
                "level": t.level,
                "path": t.path,
                "depth": t.depth,
                "is_root": t.is_root,
                "is_pinned": t.is_pinned,
                "is_archived": t.is_archived,
                "created_at": t.created_at,
                "updated_at": t.updated_at,
                "children": []
            }

        # Build hierarchy
        for t in topics:
            node = lookup[t.id]
            # If we are building a subtree, treat the target root_id as a root
            if (t.parent_id is None) or (root_id and t.id == root_id):
                roots.append(node)
            else:
                # If parent is missing (e.g. parent is deleted/filtered out), it becomes a floating root in this context
                if t.parent_id in lookup:
                    lookup[t.parent_id]["children"].append(node)
                else:
                    roots.append(node)
                    
        # Sort children
        def sort_children(node):
            node["children"].sort(key=lambda x: x["order_index"])
            for child in node["children"]:
                sort_children(child)
                
        for root in roots:
            sort_children(root)

        return [TopicTreeResponse.model_validate(r) for r in roots]

    async def get_ancestors(self, current_user: User, topic_id: uuid.UUID) -> List[Topic]:
        """Get all ancestors (parents) up to the root."""
        topic = await self.get_topic(current_user, topic_id)
        # Path is like /uuid1/uuid2/uuid3
        path_parts = [p for p in topic.path.split('/') if p]
        
        # Remove the topic itself
        if str(topic.id) in path_parts:
            path_parts.remove(str(topic.id))
            
        return await self.repo.get_ancestors(current_user.id, path_parts)

    async def get_descendants(self, current_user: User, topic_id: uuid.UUID) -> Sequence[Topic]:
        topic = await self.get_topic(current_user, topic_id)
        return await self.repo.get_descendants(current_user.id, topic.path)

    async def validate_move(self, moving_topic: Topic, new_parent: Optional[Topic]) -> None:
        """Ensure no circular references."""
        if not new_parent:
            return # Moving to root is always safe
            
        if moving_topic.id == new_parent.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A topic cannot be its own parent")
            
        # Check if the new parent's path contains the moving topic's ID
        # e.g. moving /A to /A/B/C -> new_parent path is /A/B/C. It contains "A", so invalid.
        if str(moving_topic.id) in new_parent.path:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Circular hierarchy detected")

    async def move_topic(self, current_user: User, topic_id: uuid.UUID, new_parent_id: Optional[uuid.UUID]) -> Topic:
        """Move a topic to a new parent, updating its path and all descendant paths/depths recursively."""
        topic = await self.get_topic(current_user, topic_id)
        
        # Short circuit if not actually moving
        if topic.parent_id == new_parent_id:
            return topic

        new_parent = None
        if new_parent_id:
            new_parent = await self.get_topic(current_user, new_parent_id)

        await self.validate_move(topic, new_parent)
        
        old_path = topic.path
        old_depth = topic.depth

        # Calculate new attributes for the topic
        if new_parent:
            topic.parent_id = new_parent.id
            topic.is_root = False
            topic.level = new_parent.level + 1
            topic.depth = new_parent.depth + 1
            topic.path = f"{new_parent.path}/{topic.id}"
        else:
            topic.parent_id = None
            topic.is_root = True
            topic.level = 0
            topic.depth = 0
            topic.path = f"/{topic.id}"
            
        # Place it at the end of the new siblings list
        max_idx = await self.repo.get_max_order_index(current_user.id, new_parent_id)
        topic.order_index = max_idx + 1

        # Now recursively update all descendants
        descendants = await self.repo.get_descendants(current_user.id, old_path)
        depth_diff = topic.depth - old_depth
        
        for desc in descendants:
            # Replace the old path prefix with the new path
            # e.g. old_path="/A/B", desc.path="/A/B/C" -> new_path="/Z/B/C"
            new_desc_path = desc.path.replace(old_path, topic.path, 1)
            desc.path = new_desc_path
            desc.depth += depth_diff
            desc.level += depth_diff
            
        return await self.repo.update(topic)

    async def reorder_topics(self, current_user: User, parent_id: Optional[uuid.UUID], topic_ids: List[uuid.UUID]) -> None:
        """Reorder siblings."""
        # Validate that all topics exist and belong to the same parent
        siblings = await self.repo.get_children(current_user.id, parent_id)
        sibling_ids = {s.id for s in siblings}
        
        for t_id in topic_ids:
            if t_id not in sibling_ids:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Topic {t_id} is not a valid child of this parent")
                
        if len(topic_ids) != len(sibling_ids):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide the complete list of sibling IDs to reorder")

        await self.repo.batch_update_order(current_user.id, topic_ids)

    async def search_topics(self, current_user: User, query: str) -> List[Dict[str, Any]]:
        """Search topics and attach human readable path."""
        topics = await self.repo.search(current_user.id, query)
        
        # Build human readable paths. Since path relies on IDs, we need a lookup dictionary for titles.
        # For simplicity in this implementation, we will query all topics to build the dictionary.
        # In a massive DB, it's better to fetch just the unique ancestors.
        all_topics = await self.repo.get_all_by_user(current_user.id)
        title_map = {str(t.id): t.title for t in all_topics}
        
        results = []
        for t in topics:
            path_parts = [p for p in t.path.split('/') if p]
            human_path = "/" + "/".join(title_map.get(p, "unknown") for p in path_parts)
            
            data = t.__dict__.copy()
            data["human_readable_path"] = human_path
            results.append(data)
            
        return results

    async def archive_topic(self, current_user: User, topic_id: uuid.UUID) -> Topic:
        topic = await self.get_topic(current_user, topic_id)
        topic.is_archived = True
        return await self.repo.update(topic)

    async def unarchive_topic(self, current_user: User, topic_id: uuid.UUID) -> Topic:
        topic = await self.get_topic(current_user, topic_id)
        topic.is_archived = False
        return await self.repo.update(topic)

    async def pin_topic(self, current_user: User, topic_id: uuid.UUID) -> Topic:
        topic = await self.get_topic(current_user, topic_id)
        topic.is_pinned = True
        return await self.repo.update(topic)

    async def unpin_topic(self, current_user: User, topic_id: uuid.UUID) -> Topic:
        topic = await self.get_topic(current_user, topic_id)
        topic.is_pinned = False
        return await self.repo.update(topic)
