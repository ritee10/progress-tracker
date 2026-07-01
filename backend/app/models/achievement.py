# ============================================================
# Model — Achievement & UserAchievement
# ============================================================

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, UUIDMixin, TimestampMixin


class Achievement(Base, UUIDMixin, TimestampMixin):
    """
    Achievement/badge definitions — system-managed catalog.

    Examples: "Week Warrior" (7-day streak), "DSA Century" (100 topics)
    """

    __tablename__ = "achievements"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(200), unique=True, nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    achievement_type: Mapped[str] = mapped_column(
        String(30), nullable=False, default="milestone"
    )
    category: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    criteria_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # e.g., "streak_days", "sessions_logged"
    criteria_value: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # Threshold
    xp_reward: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    rarity: Mapped[str] = mapped_column(
        String(20), nullable=False, default="common"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    # ── Relationships ────────────────────────────────────────
    user_achievements = relationship(
        "UserAchievement", back_populates="achievement", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Achievement {self.name} [{self.rarity}]>"


class UserAchievement(Base, UUIDMixin, TimestampMixin):
    """Records which users earned which achievements."""

    __tablename__ = "user_achievements"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    achievement_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("achievements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    earn_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )
    notified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # ── Relationships ────────────────────────────────────────
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

    def __repr__(self) -> str:
        return f"<UserAchievement user={self.user_id} badge={self.achievement_id}>"
