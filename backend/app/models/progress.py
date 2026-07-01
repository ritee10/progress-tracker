# ============================================================
# Model — Progress
# ============================================================

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, UUIDMixin, TimestampMixin


class Progress(Base, UUIDMixin, TimestampMixin):
    """
    A single progress log entry — records study activity for a day/session.

    Aggregated in analytics_snapshots for dashboard views.
    """

    __tablename__ = "progress"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    activity_type: Mapped[str] = mapped_column(
        String(30), nullable=False, default="practicing"
    )
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    quality_rating: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # 1-5
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    session_date: Mapped[date] = mapped_column(
        Date, nullable=False, index=True
    )
    xp_earned: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )

    # ── Relationships ────────────────────────────────────────
    user = relationship("User", back_populates="progress_records")
    skill = relationship("Skill", back_populates="progress_records")

    def __repr__(self) -> str:
        return f"<Progress {self.session_date} +{self.duration_minutes}min>"
