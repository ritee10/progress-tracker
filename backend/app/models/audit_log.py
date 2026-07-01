# ============================================================
# Model — Audit Log
# ============================================================

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, UUIDMixin, TimestampMixin


class AuditLog(Base, UUIDMixin, TimestampMixin):
    """
    Immutable audit trail of all state-changing actions.

    This table is APPEND-ONLY in production (enforced by DB trigger).
    """

    __tablename__ = "audit_logs"

    user_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True
    )  # create, update, delete, login, logout
    entity_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # "user", "skill", "task"
    entity_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    old_values: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    new_values: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(
        String(45), nullable=True  # IPv4 or IPv6
    )
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} {self.entity_type}/{self.entity_id}>"
