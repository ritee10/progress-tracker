# ============================================================
# Model — Leaderboard (Materialized/Cached View)
# ============================================================

from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, UUIDMixin, TimestampMixin


class LeaderboardEntry(Base, UUIDMixin, TimestampMixin):
    """
    Leaderboard snapshot table.

    Refreshed periodically from user profiles.
    Stored separately to avoid expensive JOINs on every leaderboard view.
    """

    __tablename__ = "leaderboard"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True, index=True
    )
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    xp_total: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    current_level: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )
    current_streak: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    longest_streak: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    skills_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    global_rank: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, index=True
    )

    def __repr__(self) -> str:
        return f"<Leaderboard #{self.global_rank} {self.username} XP={self.xp_total}>"
