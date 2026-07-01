# ============================================================
# Model — ActivityLog
# ============================================================

from sqlalchemy import ForeignKey, String, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, UUIDMixin, TimestampMixin

class ActivityLog(Base, UUIDMixin, TimestampMixin):
    """
    Tracks recent user activity for the dashboard.
    """

    __tablename__ = "activity_logs"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        Index("ix_activity_logs_user_created_at", "user_id", "created_at"),
    )

    # ── Relationships ────────────────────────────────────────
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<ActivityLog {self.activity_type} ({self.user_id})>"
