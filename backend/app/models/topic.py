# ============================================================
# Model — Topic
# ============================================================

from sqlalchemy import ForeignKey, Integer, String, Text, Boolean, Index , Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin


class Topic(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Topic Tree Adjacency List Model.
    Supports infinite nesting depth.
    """

    __tablename__ = "topics"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    skill_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parent_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=True
    )
    
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    progress_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0.0)
    completed_children: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_children: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    is_root: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # ── Indexes ───────────────────────────────────────────────
    __table_args__ = (
        Index("ix_topics_user_parent", "user_id", "parent_id"),
        Index("ix_topics_user_path", "user_id", "path"),
        Index("ix_topics_user_depth", "user_id", "depth"),
        Index("ix_topics_is_archived", "is_archived"),
        Index("ix_topics_is_pinned", "is_pinned"),
        Index("ix_topics_order_index", "order_index"),
    )

    # ── Relationships ────────────────────────────────────────
    user = relationship("User")
    
    # Self-referential relationships
    parent = relationship("Topic", remote_side="Topic.id", back_populates="children")
    children = relationship(
        "Topic", 
        back_populates="parent", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Topic {self.title} depth={self.depth}>"
