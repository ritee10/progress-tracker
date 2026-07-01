from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
#from app.models.user import User
from app.core.dependencies import CurrentUser
from app.services.search_service import SearchService
from app.schemas.search import (
    GlobalSearchResponse,
    TopicSearchResponse,
    SkillSearchResponse,
    NoteSearchResponse,
    CrossSkillSearchResponse
)

router = APIRouter(prefix="/search", tags=["Search"])

def get_search_service(db: AsyncSession = Depends(get_db)) -> SearchService:
    return SearchService(db)

@router.get("", response_model=GlobalSearchResponse)
async def global_search(
    current_user: CurrentUser,
    query: str = Query("", description="Search term"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    skill_id: Optional[UUID] = Query(None, description="Filter by Skill ID"),
    result_type: Optional[str] = Query(None, description="Filter by result type (skill, topic, note)"),
    depth_level: Optional[int] = Query(None, description="Filter topics by depth level"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    sort_by: str = Query("relevance", description="Sorting method: relevance, name_asc, name_desc"),

    service: SearchService = Depends(get_search_service)
):
    """
    Global search across Skills, Topics, and Notes.
    """
    return await service.global_search(
        user_id=current_user.id,
        query=query,
        page=page,
        limit=limit,
        skill_id=skill_id,
        result_type=result_type,
        depth_level=depth_level,
        completed=completed,
        sort_by=sort_by
    )

@router.get("/topics", response_model=TopicSearchResponse)
async def topic_search(
    current_user: CurrentUser,
    query: str = Query("", description="Search term"),
    skill_id: Optional[UUID] = Query(None, description="Filter by Skill ID"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),

    service: SearchService = Depends(get_search_service)
):
    """
    Dedicated Topic search.
    """
    return await service.topic_search(
        user_id=current_user.id,
        query=query,
        skill_id=skill_id,
        page=page,
        limit=limit
    )

@router.get("/skills", response_model=SkillSearchResponse)
async def skill_search(
    current_user: CurrentUser,
    query: str = Query("", description="Search term"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),

    service: SearchService = Depends(get_search_service)
):
    """
    Search skills.
    """
    return await service.skill_search(
        user_id=current_user.id,
        query=query,
        page=page,
        limit=limit
    )

@router.get("/notes", response_model=NoteSearchResponse)
async def note_search(
    current_user: CurrentUser,
    query: str = Query("", description="Search term"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),

    service: SearchService = Depends(get_search_service)
):
    """
    Search notes.
    """
    return await service.note_search(
        user_id=current_user.id,
        query=query,
        page=page,
        limit=limit
    )

@router.get("/cross-skill", response_model=CrossSkillSearchResponse)
async def cross_skill_search(
    current_user: CurrentUser,
    query: str = Query("", description="Search term"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),

    service: SearchService = Depends(get_search_service)
):
    """
    Search across all skills and group results by skill.
    """
    return await service.cross_skill_search(
        user_id=current_user.id,
        query=query,
        page=page,
        limit=limit
    )
