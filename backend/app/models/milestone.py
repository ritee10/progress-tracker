# ============================================================
# Model — Milestone
# ============================================================

from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, UUIDMixin, TimestampMixin


class Milestone(Base, UUIDMixin, TimestampMixin):
    """
    A measurable checkpoint within a skill.

    Example: Skill="DSA" → Milestone="Solve 50 Medium DP problems"
    """

    __tablename__ = "milestones"

    skill_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    milestone_order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    target_value: Mapped[float | None] = mapped_column(
        Integer, nullable=True
    )
    current_value: Mapped[float] = mapped_column(
        Integer, nullable=False, default=0
    )
    unit: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # "problems", "hours", "topics"
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_completed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # ── Relationships ────────────────────────────────────────
    skill = relationship("Skill", back_populates="milestones")

    def __repr__(self) -> str:
        return f"<Milestone {self.title} ({'✓' if self.is_completed else '○'})>"
