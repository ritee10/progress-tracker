# ============================================================
# Router — Leaderboard
# ============================================================

from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser, DBSession
from app.services.leaderboard_service import LeaderboardService
from app.utils.response import success_response

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get(
    "",
    response_model=dict,
    summary="Get global leaderboard",
)
async def get_leaderboard(
    current_user: CurrentUser,
    db: DBSession,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Return the global XP leaderboard. Requires authentication."""
    service = LeaderboardService(db)
    entries = await service.get_global_leaderboard(limit=limit, offset=offset)

    data = [
        {
            "user_id": str(e.user_id),
            "username": e.username,
            "full_name": e.full_name,
            "avatar_url": e.avatar_url,
            "xp_total": e.xp_total,
            "current_level": e.current_level,
            "current_streak": e.current_streak,
            "global_rank": e.global_rank,
        }
        for e in entries
    ]

    return success_response(data=data)


@router.get(
    "/me",
    response_model=dict,
    summary="Get current user's rank",
)
async def get_my_rank(current_user: CurrentUser, db: DBSession):
    """Return the current user's rank on the leaderboard."""
    service = LeaderboardService(db)
    entry = await service.get_user_rank(current_user.id)

    if not entry:
        return success_response(data=None, message="User not ranked yet")

    return success_response(
        data={
            "user_id": str(entry.user_id),
            "username": entry.username,
            "xp_total": entry.xp_total,
            "current_level": entry.current_level,
            "global_rank": entry.global_rank,
        }
    )
