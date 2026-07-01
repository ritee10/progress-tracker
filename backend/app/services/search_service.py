import uuid
from typing import Optional

from sqlalchemy import select, or_, and_, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill
from app.models.topic import Topic
from app.models.note import Note
from app.schemas.search import (
    GlobalSearchResponse,
    SearchResult,
    TopicSearchResponse,
    TopicSearchResult,
    SkillSearchResponse,
    SkillSearchResult,
    NoteSearchResponse,
    NoteSearchResult,
    CrossSkillSearchResponse,
    CrossSkillResultGroup,
)
from app.utils.search_helpers import get_pagination, format_breadcrumb, truncate_preview
from app.utils.escape import escape_like

class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def global_search(
        self,
        user_id: uuid.UUID,
        query: str,
        page: int = 1,
        limit: int = 20,
        skill_id: Optional[uuid.UUID] = None,
        result_type: Optional[str] = None,
        depth_level: Optional[int] = None,
        completed: Optional[bool] = None,
        sort_by: str = "relevance"
    ) -> GlobalSearchResponse:
        offset_val, limit_val = get_pagination(page, limit)
        
        search_results = []
        
        # 1. Search Skills
        if result_type in [None, "skill"]:
            stmt = select(Skill).where(Skill.user_id == user_id, Skill.deleted_at.is_(None))
            if query:
                safe_q = escape_like(query)
                stmt = stmt.where(or_(Skill.title.ilike(f"%{safe_q}%"), Skill.description.ilike(f"%{safe_q}%")))
            if skill_id:
                stmt = stmt.where(Skill.id == skill_id)
            if completed is not None:
                status_filter = "completed" if completed else "in_progress"
                stmt = stmt.where(Skill.status == status_filter)
            
            skills = (await self.db.execute(stmt)).scalars().all()
            for s in skills:
                matched_field = "title" if query and query.lower() in s.title.lower() else "description"
                search_results.append(SearchResult(
                    id=s.id, type="skill", name=s.title, skill_id=s.id, matched_field=matched_field
                ))
                
        # 2. Search Topics
        if result_type in [None, "topic"]:
            stmt = select(Topic).where(Topic.user_id == user_id, Topic.deleted_at.is_(None))
            if query:
                safe_q = escape_like(query)
                stmt = stmt.where(Topic.title.ilike(f"%{safe_q}%"))
            if skill_id:
                stmt = stmt.where(Topic.skill_id == skill_id)
            if depth_level is not None:
                stmt = stmt.where(Topic.depth == depth_level)
            if completed is not None:
                if completed:
                    stmt = stmt.where(Topic.progress_percent == 100)
                else:
                    stmt = stmt.where(Topic.progress_percent < 100)
                    
            topics = (await self.db.execute(stmt)).scalars().all()
            for t in topics:
                search_results.append(SearchResult(
                    id=t.id, type="topic", name=t.title, skill_id=t.skill_id, 
                    matched_field="title", parent_id=t.parent_id, path=format_breadcrumb(t.path), depth=t.depth
                ))
                
        # 3. Search Notes
        if result_type in [None, "note"]:
            stmt = select(Note).where(Note.user_id == user_id)
            if query:
                safe_q = escape_like(query)
                stmt = stmt.where(Note.content.ilike(f"%{safe_q}%"))
            if skill_id:
                stmt = stmt.where(Note.skill_id == skill_id)
            # notes don't have completed or depth_level directly
            
            notes = (await self.db.execute(stmt)).scalars().all()
            for n in notes:
                search_results.append(SearchResult(
                    id=n.id, type="note", name=truncate_preview(n.content), skill_id=n.skill_id,
                    matched_field="content"
                ))

        # Sorting
        if sort_by == "name_asc":
            search_results.sort(key=lambda x: x.name.lower())
        elif sort_by == "name_desc":
            search_results.sort(key=lambda x: x.name.lower(), reverse=True)
        elif sort_by == "relevance" and query:
            search_results.sort(key=lambda x: (query.lower() not in x.name.lower(), len(x.name)))

        # NOTE: global_search loads all matched results into memory for cross-type sorting.
        # This is acceptable for moderate result sets (skills+topics+notes are bounded per user).
        # For very large datasets, implement type-specific paginated search instead.
        total = len(search_results)
        paginated_items = search_results[offset_val: offset_val + limit_val]

        return GlobalSearchResponse(total=total, page=page, limit=limit, items=paginated_items)

    async def topic_search(
        self, user_id: uuid.UUID, query: Optional[str] = None, skill_id: Optional[uuid.UUID] = None,
        page: int = 1, limit: int = 20
    ) -> TopicSearchResponse:
        offset_val, limit_val = get_pagination(page, limit)

        base_stmt = select(Topic).where(Topic.user_id == user_id, Topic.deleted_at.is_(None))
        if query:
            safe_q = escape_like(query)
            base_stmt = base_stmt.where(Topic.title.ilike(f"%{safe_q}%"))
        if skill_id:
            base_stmt = base_stmt.where(Topic.skill_id == skill_id)

        # COUNT via SQL — never load all rows to count in Python
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = (await self.db.scalar(count_stmt)) or 0

        # Paginated data query
        data_stmt = base_stmt.order_by(Topic.created_at.desc()).offset(offset_val).limit(limit_val)
        topics = (await self.db.execute(data_stmt)).scalars().all()

        items = [TopicSearchResult(
            id=t.id, title=t.title, skill_id=t.skill_id, parent_id=t.parent_id,
            depth=t.depth, path=format_breadcrumb(t.path), level=t.level
        ) for t in topics]

        return TopicSearchResponse(total=total, page=page, limit=limit, items=items)

    async def skill_search(
        self, user_id: uuid.UUID, query: Optional[str] = None, page: int = 1, limit: int = 20
    ) -> SkillSearchResponse:
        offset_val, limit_val = get_pagination(page, limit)

        base_stmt = select(Skill).where(Skill.user_id == user_id, Skill.deleted_at.is_(None))
        if query:
            safe_q = escape_like(query)
            base_stmt = base_stmt.where(or_(Skill.title.ilike(f"%{safe_q}%"), Skill.description.ilike(f"%{safe_q}%")))

        # COUNT via SQL
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = (await self.db.scalar(count_stmt)) or 0

        data_stmt = base_stmt.order_by(Skill.created_at.desc()).offset(offset_val).limit(limit_val)
        skills = (await self.db.execute(data_stmt)).scalars().all()

        items = [SkillSearchResult(
            id=s.id, title=s.title, description=s.description, category=s.category,
            difficulty=s.difficulty, status=s.status
        ) for s in skills]

        return SkillSearchResponse(total=total, page=page, limit=limit, items=items)

    async def note_search(
        self, user_id: uuid.UUID, query: Optional[str] = None, page: int = 1, limit: int = 20
    ) -> NoteSearchResponse:
        offset_val, limit_val = get_pagination(page, limit)

        base_stmt = select(Note).where(Note.user_id == user_id)
        if query:
            safe_q = escape_like(query)
            base_stmt = base_stmt.where(Note.content.ilike(f"%{safe_q}%"))

        # COUNT via SQL
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = (await self.db.scalar(count_stmt)) or 0

        data_stmt = base_stmt.order_by(Note.created_at.desc()).offset(offset_val).limit(limit_val)
        notes = (await self.db.execute(data_stmt)).scalars().all()

        items = [NoteSearchResult(
            id=n.id, skill_id=n.skill_id, topic_id=n.topic_id,
            content_preview=truncate_preview(n.content), urls=n.urls
        ) for n in notes]

        return NoteSearchResponse(total=total, page=page, limit=limit, items=items)

    async def cross_skill_search(
        self, user_id: uuid.UUID, query: Optional[str] = None, page: int = 1, limit: int = 20
    ) -> CrossSkillSearchResponse:
        # Fetch global results with a reasonable cap instead of unbounded 1000-record fetch
        MAX_CROSS_RESULTS = 200
        global_res = await self.global_search(user_id, query=query or "", page=1, limit=MAX_CROSS_RESULTS)

        # Fetch skill details for grouping in a single IN query
        skill_ids = list({item.skill_id for item in global_res.items if item.skill_id})
        skill_map: dict = {}
        if skill_ids:
            stmt = select(Skill.id, Skill.title).where(Skill.id.in_(skill_ids))
            rows = (await self.db.execute(stmt)).all()
            skill_map = {r[0]: r[1] for r in rows}

        grouped: dict = {}
        for item in global_res.items:
            grouped.setdefault(item.skill_id, []).append(item)

        groups = [
            CrossSkillResultGroup(
                skill_id=sid, skill_title=skill_map.get(sid, "Unknown Skill"), results=res_list
            )
            for sid, res_list in grouped.items()
        ]

        # Paginate groups
        total = len(groups)
        offset_val, limit_val = get_pagination(page, limit)
        paginated_groups = groups[offset_val: offset_val + limit_val]

        return CrossSkillSearchResponse(total=total, page=page, limit=limit, items=paginated_groups)
