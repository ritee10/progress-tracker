# ============================================================
# Router — Dashboard (Phase 13)
# ============================================================

from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser, DBSession
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import (
    DashboardResponse,
    ActivityFeedResponse,
    LastSeenRequest
)
from app.utils.response import success_response

router = APIRouter(tags=["Dashboard"])

@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Get unified dashboard metrics and data",
)
async def get_dashboard(current_user: CurrentUser, db: DBSession):
    """
    Return a comprehensive overview of the user's progress, 
    including pinned skills, overdue skills, last seen, statistics, and recent activity.
    """
    service = DashboardService(db)
    data = await service.get_full_dashboard(current_user.id)
    return data

@router.get(
    "/dashboard/activity",
    response_model=ActivityFeedResponse,
    summary="Get paginated recent activity",
)
async def get_dashboard_activity(
    current_user: CurrentUser,
    db: DBSession,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    service = DashboardService(db)
    activities = await service.get_activities(current_user.id, limit=limit, offset=offset)
    return {
        "activities": activities,
        "total": len(activities)
    }

@router.post(
    "/dashboard/last-seen",
    summary="Update the user's last seen tracking point",
)
async def update_last_seen(
    req: LastSeenRequest,
    current_user: CurrentUser,
    db: DBSession
):
    service = DashboardService(db)
    await service.update_last_seen(current_user.id, req.skillId, req.topicId)
    return success_response(message="Last seen updated")
