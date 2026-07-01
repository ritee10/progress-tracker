# ============================================================
# Router — Milestones
# ============================================================

import uuid

from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DBSession
from app.schemas.milestone import MilestoneCreate, MilestoneResponse, MilestoneUpdate
from app.utils.response import success_response

# NOTE: Milestone service follows the same pattern as SkillService.
# For brevity, direct DB operations are shown here; extract to a
# service class as the codebase grows.

from fastapi import HTTPException, status
from sqlalchemy import select
from app.models.milestone import Milestone
from app.models.skill import Skill

router = APIRouter(prefix="/milestones", tags=["Milestones"])


@router.post(
    "",
    response_model=dict,
    status_code=201,
    summary="Create a milestone for a skill",
)
async def create_milestone(
    data: MilestoneCreate, current_user: CurrentUser, db: DBSession
):
    """Add a milestone checkpoint to an existing skill."""
    # Verify the skill belongs to this user
    result = await db.execute(
        select(Skill).where(
            Skill.id == data.skill_id,
            Skill.user_id == current_user.id,
            Skill.deleted_at == None,  # noqa
        )
    )
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    milestone = Milestone(
        skill_id=data.skill_id,
        title=data.title,
        description=data.description,
        milestone_order=data.milestone_order,
        target_value=data.target_value,
        unit=data.unit,
        target_date=data.target_date,
    )
    db.add(milestone)
    await db.flush()
    await db.refresh(milestone)

    return success_response(
        data=MilestoneResponse.model_validate(milestone).model_dump(mode="json"),
        message="Milestone created",
    )


@router.put(
    "/{milestone_id}",
    response_model=dict,
    summary="Update a milestone",
)
async def update_milestone(
    milestone_id: uuid.UUID,
    data: MilestoneUpdate,
    current_user: CurrentUser,
    db: DBSession,
):
    """Update an existing milestone."""
    milestone = await _get_user_milestone(db, milestone_id, current_user.id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(milestone, field, value)

    await db.flush()
    await db.refresh(milestone)

    return success_response(
        data=MilestoneResponse.model_validate(milestone).model_dump(mode="json"),
        message="Milestone updated",
    )


@router.delete(
    "/{milestone_id}",
    response_model=dict,
    summary="Delete a milestone",
)
async def delete_milestone(
    milestone_id: uuid.UUID, current_user: CurrentUser, db: DBSession
):
    """Hard-delete a milestone."""
    milestone = await _get_user_milestone(db, milestone_id, current_user.id)
    await db.delete(milestone)
    await db.flush()
    return success_response(message="Milestone deleted")


async def _get_user_milestone(db, milestone_id, user_id) -> Milestone:
    """Fetch a milestone ensuring it belongs to the user via its parent skill."""
    result = await db.execute(
        select(Milestone)
        .join(Skill, Skill.id == Milestone.skill_id)
        .where(
            Milestone.id == milestone_id,
            Skill.user_id == user_id,
            Skill.deleted_at == None,  # noqa
        )
    )
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return milestone
