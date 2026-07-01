# ============================================================
# Router — Achievements
# ============================================================

from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DBSession
from app.schemas.dashboard import RecentAchievement
from app.services.achievement_service import AchievementService
from app.utils.response import success_response

router = APIRouter(prefix="/achievements", tags=["Achievements"])


@router.get(
    "",
    response_model=dict,
    summary="Get user achievements",
)
async def get_user_achievements(current_user: CurrentUser, db: DBSession):
    """Return all achievements earned by the user."""
    service = AchievementService(db)
    user_achievements = await service.get_user_achievements(current_user.id)

    data = []
    for ua in user_achievements:
        if ua.achievement:
            data.append(
                RecentAchievement(
                    id=ua.achievement.id,
                    name=ua.achievement.name,
                    description=ua.achievement.description,
                    icon_url=ua.achievement.icon_url,
                    rarity=ua.achievement.rarity,
                    earned_at=str(ua.created_at),
                ).model_dump(mode="json")
            )

    return success_response(data=data)


@router.get(
    "/catalog",
    response_model=dict,
    summary="Get all available achievements",
)
async def get_achievement_catalog(current_user: CurrentUser, db: DBSession):
    """Return all available achievements in the system. Requires authentication."""
    service = AchievementService(db)
    catalog = await service.get_all_achievements()
    
    data = [
        {
            "id": str(a.id),
            "name": a.name,
            "description": a.description,
            "icon_url": a.icon_url,
            "rarity": a.rarity,
            "criteria_type": a.criteria_type,
            "criteria_value": a.criteria_value,
            "xp_reward": a.xp_reward,
        }
        for a in catalog
    ]

    return success_response(data=data)
