# ============================================================
# Model — Topic Completion
# ============================================================

from sqlalchemy import ForeignKey, Boolean, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, UUIDMixin, TimestampMixin


class TopicCompletion(Base, UUIDMixin, TimestampMixin):
    """
    Tracks the completion status of a leaf topic for a user.
    """

    __tablename__ = "topic_completions"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    node_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False
    )
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Indexes & Constraints ──────────────────────────────
    __table_args__ = (
        Index("uix_topic_completions_user_node", "user_id", "node_id", unique=True),
    )

    # ── Relationships ────────────────────────────────────────
    user = relationship("User")
    node = relationship("Topic")
