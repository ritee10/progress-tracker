import uuid
import logging
from app.core.events import events
from app.database.session import async_session_factory
from app.services.streak_service import StreakService

logger = logging.getLogger(__name__)

async def handle_leaf_completed(user_id: uuid.UUID, node_id: uuid.UUID, **kwargs):
    """
    Event handler for when a leaf topic is completed.
    Triggers the Streak System to record the activity.
    """
    async with async_session_factory() as session:
        try:
            streak_svc = StreakService(session)
            await streak_svc.recordActivity(user_id=user_id)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Error handling leaf_completed_event for user {user_id}: {e}")

def register_events():
    """Register all application event subscriptions here."""
    events.subscribe("leaf_completed_event", handle_leaf_completed)
