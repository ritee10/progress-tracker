# ============================================================
# Model — Note
# ============================================================

from sqlalchemy import ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, UUIDMixin, TimestampMixin


class Note(Base, UUIDMixin, TimestampMixin):
    """
    Represents a learning note attached to a leaf topic.
    """

    __tablename__ = "notes"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    skill_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True
    )
    topic_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    content: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    urls: Mapped[list[str]] = mapped_column(JSONB, server_default='[]', nullable=False)

    # ── Indexes ──────────────────────────────────────────────
    __table_args__ = (
        Index("ix_notes_user_skill", "user_id", "skill_id"),
        Index("ix_notes_user_topic", "user_id", "topic_id"),
    )

    # ── Relationships ────────────────────────────────────────
    user = relationship("User")
    skill = relationship("Skill")
    topic = relationship("Topic")
