# ============================================================
# Models — Streak
# ============================================================

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, UUIDMixin, TimestampMixin


class StreakDay(Base, UUIDMixin, TimestampMixin):
    """
    STREAK_DAY
    Records a day where the user completed at least one leaf topic.
    """

    __tablename__ = "streak_days"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    streak_date: Mapped[date] = mapped_column(
        Date, nullable=False, index=True
    )
    completed_topics_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )

    # ── Relationships ────────────────────────────────────────
    user = relationship("User", back_populates="streak_days")

    # ── Constraints ──────────────────────────────────────────
    __table_args__ = (
        UniqueConstraint("user_id", "streak_date", name="uix_user_streak_date"),
    )

    def __repr__(self) -> str:
        return f"<StreakDay {self.user_id} on {self.streak_date} ({self.completed_topics_count} topics)>"


class StreakStats(Base, UUIDMixin, TimestampMixin):
    """
    STREAK_STATS
    Maintains running totals for streak tracking (Current, Longest).
    """

    __tablename__ = "streak_stats"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    current_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_activity_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # ── Relationships ────────────────────────────────────────
    user = relationship("User", back_populates="streak_stats")

    def __repr__(self) -> str:
        return f"<StreakStats user={self.user_id} current={self.current_streak} longest={self.longest_streak}>"
