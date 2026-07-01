# ============================================================
# Model — User
# ============================================================

import uuid
from datetime import datetime

from sqlalchemy import Boolean, String, Text, Integer, DateTime , ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin


class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Core user identity table."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False, default="EMAIL")
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default="USER"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    xp_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Relationships ────────────────────────────────────────
    skills = relationship("Skill", back_populates="user", lazy="selectin")
    tasks = relationship("Task", back_populates="user", lazy="selectin")
    progress_records = relationship(
        "Progress", back_populates="user", lazy="selectin"
    )
    streak_days = relationship("StreakDay", back_populates="user", lazy="selectin")
    streak_stats = relationship("StreakStats", back_populates="user", lazy="selectin", uselist=False)
    xp_records = relationship("XPRecord", back_populates="user", lazy="selectin")
    achievements = relationship(
        "UserAchievement", back_populates="user", lazy="selectin"
    )
    notifications = relationship(
        "Notification", back_populates="user", lazy="selectin"
    )
    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.email})>"


class UserDashboardState(Base, TimestampMixin):
    """Stores temporary preferences and last seen state for a user's dashboard."""
    __tablename__ = "user_dashboard_states"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    last_seen_skill_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    last_seen_topic_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("User")

