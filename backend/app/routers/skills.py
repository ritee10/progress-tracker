# ============================================================
# Router — Skills
# ============================================================

import uuid
from typing import Optional

from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser, DBSession
from app.schemas.skill import SkillCreate, SkillUpdate
from app.services.skill_service import SkillService
from app.utils.pagination import PaginationParams, paginate
from app.utils.response import success_response

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.post(
    "",
    response_model=dict,
    status_code=201,
    summary="Create a new tracked skill",
)
async def create_skill(
    data: SkillCreate, current_user: CurrentUser, db: DBSession
):
    """Add a new skill to the user's tracking list."""
    service = SkillService(db)
    skill = await service.create_skill(current_user, data)
    return success_response(data=skill.model_dump(mode="json"), message="Skill created")


@router.get(
    "/stats",
    response_model=dict,
    summary="Get skill statistics",
)
async def get_skill_stats(current_user: CurrentUser, db: DBSession):
    """Fetch aggregated statistics about user's skills."""
    service = SkillService(db)
    stats = await service.get_statistics(current_user)
    return success_response(data=stats.model_dump(mode="json"))


@router.get(
    "/upcoming",
    response_model=dict,
    summary="Get upcoming skill deadlines",
)
async def get_upcoming_deadlines(current_user: CurrentUser, db: DBSession):
    """Fetch next 10 upcoming skill deadlines."""
    service = SkillService(db)
    skills = await service.repo.get_upcoming_deadlines(current_user.id)
    return success_response(data=[s.model_dump(mode="json") for s in skills])


@router.get(
    "",
    response_model=dict,
    summary="List all tracked skills",
)
async def list_skills(
    current_user: CurrentUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    is_pinned: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$")
):
    """Fetch the user's skills with advanced filtering, sorting, and pagination."""
    service = SkillService(db)
    offset = (page - 1) * limit
    
    items = await service.repo.list_skills(
        user_id=current_user.id,
        offset=offset,
        limit=limit,
        status=status,
        difficulty=difficulty,
        priority=priority,
        category=category,
        is_pinned=is_pinned,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    total = await service.repo.count_skills(
        user_id=current_user.id,
        status=status,
        difficulty=difficulty,
        priority=priority,
        category=category,
        is_pinned=is_pinned,
        search=search
    )
    
    # Normally we'd serialize via Schema first, doing simplified dict dump for generic success wrapper
    from app.schemas.skill import SkillResponse
    serialized_items = [SkillResponse.model_validate(i).model_dump(mode="json") for i in items]
    
    pagination_data = paginate(items=serialized_items, total=total, page=page, page_size=limit)
    return success_response(data=pagination_data.model_dump(mode="json"))


@router.get(
    "/{skill_id}",
    response_model=dict,
    summary="Get a specific skill",
)
async def get_skill(
    skill_id: uuid.UUID, current_user: CurrentUser, db: DBSession
):
    """Fetch a single skill by ID."""
    service = SkillService(db)
    skill = await service.get_skill(current_user, skill_id)
    from app.schemas.skill import SkillResponse
    return success_response(data=SkillResponse.model_validate(skill).model_dump(mode="json"))


@router.put(
    "/{skill_id}",
    response_model=dict,
    summary="Update a skill",
)
async def update_skill(
    skill_id: uuid.UUID,
    data: SkillUpdate,
    current_user: CurrentUser,
    db: DBSession,
):
    """Update an existing tracked skill."""
    service = SkillService(db)
    skill = await service.update_skill(current_user, skill_id, data)
    from app.schemas.skill import SkillResponse
    return success_response(data=SkillResponse.model_validate(skill).model_dump(mode="json"), message="Skill updated")


@router.delete(
    "/{skill_id}",
    response_model=dict,
    summary="Delete a skill",
)
async def delete_skill(
    skill_id: uuid.UUID, current_user: CurrentUser, db: DBSession
):
    """Soft-delete a tracked skill."""
    service = SkillService(db)
    result = await service.delete_skill(current_user, skill_id)
    return success_response(message=result["message"])


@router.patch(
    "/{skill_id}/pin",
    response_model=dict,
    summary="Pin a skill",
)
async def pin_skill(
    skill_id: uuid.UUID, current_user: CurrentUser, db: DBSession
):
    """Pin a skill to the top of the list."""
    service = SkillService(db)
    skill = await service.pin_skill(current_user, skill_id)
    from app.schemas.skill import SkillResponse
    return success_response(data=SkillResponse.model_validate(skill).model_dump(mode="json"), message="Skill pinned")


@router.patch(
    "/{skill_id}/unpin",
    response_model=dict,
    summary="Unpin a skill",
)
async def unpin_skill(
    skill_id: uuid.UUID, current_user: CurrentUser, db: DBSession
):
    """Unpin a skill from the top of the list."""
    service = SkillService(db)
    skill = await service.unpin_skill(current_user, skill_id)
    from app.schemas.skill import SkillResponse
    return success_response(data=SkillResponse.model_validate(skill).model_dump(mode="json"), message="Skill unpinned")
