# ============================================================
# Constants — Application-wide Enums and Static Values
# ============================================================

from enum import Enum


class UserRole(str, Enum):
    """User roles for RBAC."""
    USER = "user"
    PREMIUM = "premium"
    MENTOR = "mentor"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class SkillStatus(str, Enum):
    """Lifecycle status for skill progress."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"


class GoalStatus(str, Enum):
    """Lifecycle status for user goals."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    ABANDONED = "abandoned"


class TaskStatus(str, Enum):
    """Status for study plan tasks."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class SkillDifficulty(str, Enum):
    """Difficulty levels for skills."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class SkillPriority(str, Enum):
    """Priority levels for skills."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActivityType(str, Enum):
    """Types of study activities."""
    READING = "reading"
    WATCHING = "watching"
    CODING = "coding"
    PRACTICING = "practicing"
    REVISING = "revising"
    PROJECT_WORK = "project_work"
    ASSESSMENT = "assessment"
    NOTE_TAKING = "note_taking"


class NotificationType(str, Enum):
    """Notification categories."""
    REMINDER = "reminder"
    ACHIEVEMENT = "achievement"
    STREAK_ALERT = "streak_alert"
    RECOMMENDATION = "recommendation"
    SYSTEM = "system"
    MILESTONE = "milestone"
    WEEKLY_DIGEST = "weekly_digest"


class AchievementRarity(str, Enum):
    """Badge rarity tiers."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


# ── Pagination Defaults ──────────────────────────────────────
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# ── XP Configuration ────────────────────────────────────────
XP_PER_MINUTE = 1
XP_QUALITY_MULTIPLIER = 2
XP_STREAK_BONUS_THRESHOLD = 7   # Days before streak bonus kicks in
XP_STREAK_MULTIPLIER = 1.5

# ── Streak Configuration ────────────────────────────────────
MAX_STREAK_FREEZE_PER_MONTH = 2

# ── API Versioning ───────────────────────────────────────────
API_V1_PREFIX = "/api/v1"
