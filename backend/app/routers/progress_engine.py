# ============================================================
# Router — Progress
# ============================================================

import uuid

from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DBSession
from app.schemas.progress import (
    ProgressToggleRequest, ProgressToggleResponse,
    SkillProgressResponse, NodeProgressResponse
)
from app.services.progress_service import ProgressCalculationService
from app.utils.response import success_response
from sqlalchemy.future import select
from app.models.topic import Topic
from fastapi import HTTPException

router = APIRouter(prefix="/progress", tags=["Progress Tracking Engine"])


@router.post(
    "/toggle",
    response_model=dict,
    summary="Toggle node completion status",
)
async def toggle_completion(data: ProgressToggleRequest, current_user: CurrentUser, db: DBSession):
    service = ProgressCalculationService(db)
    result = await service.toggle_completion(current_user, data.node_id)
    return success_response(data=result.model_dump(mode="json"))


@router.post(
    "/complete",
    response_model=dict,
    summary="Mark node complete",
)
async def mark_complete(data: ProgressToggleRequest, current_user: CurrentUser, db: DBSession):
    service = ProgressCalculationService(db)
    result = await service.mark_complete(current_user, data.node_id)
    return success_response(data=result.model_dump(mode="json"))


@router.post(
    "/incomplete",
    response_model=dict,
    summary="Mark node incomplete",
)
async def mark_incomplete(data: ProgressToggleRequest, current_user: CurrentUser, db: DBSession):
    service = ProgressCalculationService(db)
    result = await service.mark_incomplete(current_user, data.node_id)
    return success_response(data=result.model_dump(mode="json"))


@router.get(
    "/skill/{skill_id}",
    response_model=dict,
    summary="Get full progress report for a skill",
)
async def get_skill_progress(skill_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    from app.models.skill import Skill
    result = await db.execute(select(Skill).where(Skill.id == skill_id, Skill.user_id == current_user.id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
        
    data = SkillProgressResponse(
        skill_id=skill.id,
        progress_percent=float(skill.progress_percent),
        completed_nodes=skill.completed_nodes,
        total_nodes=skill.total_nodes
    )
    return success_response(data=data.model_dump(mode="json"))


@router.get(
    "/node/{node_id}",
    response_model=dict,
    summary="Get progress report for a specific topic node",
)
async def get_node_progress(node_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    result = await db.execute(select(Topic).where(Topic.id == node_id, Topic.user_id == current_user.id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Node not found")
        
    data = NodeProgressResponse(
        node_id=topic.id,
        progress_percent=float(topic.progress_percent)
    )
    return success_response(data=data.model_dump(mode="json"))


@router.post(
    "/recalculate-skill/{skill_id}",
    response_model=dict,
    summary="Bulk recalculate all progress for a skill",
)
async def recalculate_skill_progress(skill_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    """Admin or repair endpoint to rebuild progress if corruption occurs."""
    # First recalculate all topics bottom-up (For simplicity here, we assume the calculation engine triggers will handle it 
    # if we just iterate all leaves. A true bulk rebuild would wipe the fields and sum them up again.)
    service = ProgressCalculationService(db)
    progress = await service.recalculate_skill(current_user.id, skill_id)
    return success_response(message=f"Skill recalculated to {progress}%")
