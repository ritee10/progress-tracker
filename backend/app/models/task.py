# ============================================================
# Model — Task
# ============================================================

from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, UUIDMixin, TimestampMixin


class Task(Base, UUIDMixin, TimestampMixin):
    """
    A discrete study task within a skill.

    Example: "Read chapter 5 on Graph BFS/DFS",
             "Solve 3 medium sliding-window problems"
    """

    __tablename__ = "tasks"

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
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )
    priority: Mapped[int] = mapped_column(
        Integer, nullable=False, default=3
    )  # 1=highest, 5=lowest
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    estimated_minutes: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    actual_minutes: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    is_recurring: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    completed_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    # ── Relationships ────────────────────────────────────────
    user = relationship("User", back_populates="tasks")
    skill = relationship("Skill", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<Task {self.title} ({self.status})>"
