# ============================================================
# Router — Users
# ============================================================

import uuid

from fastapi import APIRouter, Depends

from app.core.constants import UserRole
from app.core.dependencies import CurrentUser, DBSession, require_role
from app.schemas.user import UserUpdate
from app.services.user_service import UserService
from app.utils.response import success_response

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=dict,
    summary="Get current user profile",
)
async def get_my_profile(current_user: CurrentUser, db: DBSession):
    """Return the authenticated user's full profile."""
    service = UserService(db)
    profile = await service.get_profile(current_user)
    return success_response(data=profile.model_dump(mode="json"))


@router.patch(
    "/me",
    response_model=dict,
    summary="Update current user profile",
)
async def update_my_profile(
    data: UserUpdate, current_user: CurrentUser, db: DBSession
):
    """Update the authenticated user's profile fields."""
    service = UserService(db)
    profile = await service.update_profile(current_user, data)
    return success_response(data=profile.model_dump(mode="json"), message="Profile updated")


@router.delete(
    "/me",
    response_model=dict,
    summary="Deactivate current user account",
)
async def deactivate_account(current_user: CurrentUser, db: DBSession):
    """Soft-delete the authenticated user's account (30-day recovery window)."""
    service = UserService(db)
    result = await service.deactivate_account(current_user)
    return success_response(message=result["message"])


@router.get(
    "/{user_id}",
    response_model=dict,
    summary="Get user by ID (admin)",
    dependencies=[Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN))],
)
async def get_user_by_id(user_id: uuid.UUID, db: DBSession):
    """Admin endpoint to fetch any user by ID."""
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    return success_response(data=user.model_dump(mode="json"))
