# ============================================================
# Model — Skill
# ============================================================

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.database.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin


class Skill(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    A skill being tracked by a user.
    """

    __tablename__ = "skills"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    difficulty: Mapped[str] = mapped_column(
        String(20), nullable=False, default="beginner"
    )
    target_hours: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0)
    estimated_completion_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="not_started", index=True
    )
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, default="medium", index=True
    )
    progress_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0.0)
    completed_nodes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_nodes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    is_pinned: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )
    color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_activity_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    # ── Relationships ────────────────────────────────────────
    user = relationship("User", back_populates="skills")
    milestones = relationship(
        "Milestone", back_populates="skill", lazy="selectin",
        cascade="all, delete-orphan"
    )
    tasks = relationship(
        "Task", back_populates="skill", lazy="selectin",
        cascade="all, delete-orphan"
    )
    progress_records = relationship(
        "Progress", back_populates="skill", lazy="selectin",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Skill {self.title} ({self.status})>"
