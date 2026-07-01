# ============================================================
# Models Package — Import All Models
# ============================================================
# Import all models here so that Alembic and Base.metadata
# can discover every table for migration auto-generation.
# ============================================================

from app.models.user import User
from app.models.skill import Skill
from app.models.milestone import Milestone
from app.models.task import Task
from app.models.progress import Progress
from app.models.streak import StreakDay, StreakStats
from app.models.import_job import PdfImportJob
from app.models.xp import XPRecord
from app.models.achievement import Achievement, UserAchievement
from app.models.leaderboard import LeaderboardEntry
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.models.refresh_token import RefreshToken
from app.models.topic import Topic
from app.models.topic_completion import TopicCompletion
from app.models.note import Note
from app.models.activity import ActivityLog
from app.models.user import UserDashboardState

__all__ = [
    "User",
    "Skill",
    "Milestone",
    "Task",
    "Progress",
    "StreakDay",
    "StreakStats",
    "PdfImportJob",
    "XPRecord",
    "Achievement",
    "UserAchievement",
    "LeaderboardEntry",
    "Notification",
    "AuditLog",
    "RefreshToken",
    "Topic",
    "TopicCompletion",
    "Note",
    "ActivityLog",
    "UserDashboardState",
]
