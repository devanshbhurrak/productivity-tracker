import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Index, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.user import GUID, utcnow


class TimeSession(Base):
    __tablename__ = "time_sessions"

    id = Column(GUID(), primary_key=True, default=lambda: uuid.uuid4())
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(GUID(), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, nullable=True)  # seconds, null for active
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    user = relationship("User", back_populates="time_sessions")
    task = relationship("Task", back_populates="time_sessions")

    __table_args__ = (
        Index("ix_time_sessions_user_id", "user_id"),
        Index("ix_time_sessions_task_id", "task_id"),
        Index("ix_time_sessions_started_at", "started_at"),
        Index("ix_time_sessions_ended_at", "ended_at"),
        Index("ix_time_sessions_user_task", "user_id", "task_id"),
        CheckConstraint("duration IS NULL OR duration >= 0", name="ck_time_sessions_duration_non_negative"),
        CheckConstraint("ended_at IS NULL OR ended_at >= started_at", name="ck_time_sessions_ended_after_start"),
        # Note: partial unique index for one active per user is created via migration for PostgreSQL.
        # For SQLite we enforce at application layer; but we also add a conditional unique constraint attempt via
        # creating index manually in create_all_tables fallback.
    )
