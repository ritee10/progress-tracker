# ============================================================
# Model — XP Record
# ============================================================

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, UUIDMixin, TimestampMixin


class XPRecord(Base, UUIDMixin, TimestampMixin):
    """
    Individual XP transaction log.

    Every XP gain or loss is logged here for auditability.
    Aggregated total lives in the user profile cache.
    """

    __tablename__ = "xp_records"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "study_session", "achievement", "streak_bonus"
    source_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )  # Reference to the source entity
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    # ── Relationships ────────────────────────────────────────
    user = relationship("User", back_populates="xp_records")

    def __repr__(self) -> str:
        return f"<XP +{self.amount} ({self.source_type})>"
