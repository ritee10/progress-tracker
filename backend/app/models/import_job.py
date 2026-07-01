# ============================================================
# Model — Import Job
# ============================================================

from datetime import datetime

from sqlalchemy import ForeignKey, String, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, UUIDMixin, TimestampMixin


class PdfImportJob(Base, UUIDMixin, TimestampMixin):
    """
    Tracks the status and results of a PDF Import process.
    """

    __tablename__ = "pdf_import_jobs"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    tree_data: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True)
    
    total_topics: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_topics: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_topics: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Relationships ────────────────────────────────────────
    user = relationship("User")
    skill = relationship("Skill")

    def __repr__(self) -> str:
        return f"<PdfImportJob {self.filename} ({self.status})>"
