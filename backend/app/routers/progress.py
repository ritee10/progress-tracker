# ============================================================
# Router — Progress
# ============================================================

from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DBSession
from app.schemas.progress import ProgressCreate
from app.services.progress_service import ProgressService
from app.services.streak_service import StreakService
from app.services.xp_service import XPService
from app.utils.date_utils import today_utc
from app.utils.response import success_response

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.post(
    "/update",
    response_model=dict,
    status_code=201,
    summary="Log a study session",
)
async def log_progress(
    data: ProgressCreate, current_user: CurrentUser, db: DBSession
):
    """
    Record a study session with duration, activity type, and quality.

    Automatically:
    - Calculates and awards XP
    - Updates daily streak
    - Checks for new achievement eligibility
    """
    progress_svc = ProgressService(db)
    streak_svc = StreakService(db)
    xp_svc = XPService(db)

    # 1. Log the progress entry
    progress = await progress_svc.log_progress(current_user, data)

    # 2. Record XP transaction
    await xp_svc.award_xp(
        user_id=current_user.id,
        amount=progress.xp_earned,
        source_type="study_session",
        source_id=progress.id,
        description=f"{data.activity_type} for {data.duration_minutes} min",
    )

    return success_response(
        data=progress.model_dump(mode="json"),
        message=f"+{progress.xp_earned} XP earned",
    )


@router.get(
    "/summary",
    response_model=dict,
    summary="Get progress summary",
)
async def get_progress_summary(current_user: CurrentUser, db: DBSession):
    """
    Aggregated progress summary including:
    - Total study time, sessions, XP
    - Current/longest streak
    - Skill completion counts
    - Active days this month
    """
    service = ProgressService(db)
    summary = await service.get_summary(current_user)

    # Enrich with streak data
    streak_svc = StreakService(db)
    stats = await streak_svc.getStats(current_user.id)
    summary.current_streak = stats.get("currentStreak", 0)
    summary.longest_streak = stats.get("longestStreak", 0)

    return success_response(data=summary.model_dump())
