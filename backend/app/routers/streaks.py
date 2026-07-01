# ============================================================
# Router — Streaks
# ============================================================

from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser, DBSession
from app.services.streak_service import StreakService

router = APIRouter(prefix="/streaks", tags=["Streaks"])

@router.get(
    "",
    response_model=dict,
    summary="Get user's basic streak info",
)
async def get_streak_info(current_user: CurrentUser, db: DBSession):
    """Return the user's basic streak stats."""
    service = StreakService(db)
    stats = await service.getStats(current_user.id)
    return {
        "currentStreak": stats.get("currentStreak"),
        "longestStreak": stats.get("longestStreak"),
        "lastActivityDate": stats.get("lastActivityDate"),
    }


@router.get(
    "/heatmap",
    response_model=list,
    summary="Get user's activity heatmap",
)
async def get_heatmap(
    current_user: CurrentUser, 
    db: DBSession,
    days: int = Query(365, description="Number of days to fetch data for")
):
    """Return an array of objects representing date and completed topics count."""
    service = StreakService(db)
    return await service.getHeatmap(current_user.id, days=days)


@router.get(
    "/calendar",
    response_model=list,
    summary="Get user's streak calendar dates",
)
async def get_calendar(current_user: CurrentUser, db: DBSession):
    """Return an array of dates where the user was active."""
    service = StreakService(db)
    return await service.getCalendar(current_user.id)


@router.get(
    "/stats",
    response_model=dict,
    summary="Get detailed streak stats",
)
async def get_streak_stats(current_user: CurrentUser, db: DBSession):
    """Return detailed statistics: current, longest, total active days, total topics."""
    service = StreakService(db)
    stats = await service.getStats(current_user.id)
    return stats
