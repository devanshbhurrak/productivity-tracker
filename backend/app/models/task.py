import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum as SAEnum, Index, CheckConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.user import GUID, utcnow


class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(GUID(), primary_key=True, default=lambda: uuid.uuid4())
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SAEnum(TaskStatus, name="task_status", native_enum=False), nullable=False, default=TaskStatus.PENDING)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="tasks")
    time_sessions = relationship("TimeSession", back_populates="task", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_tasks_user_id", "user_id"),
        Index("ix_tasks_user_status", "user_id", "status"),
        Index("ix_tasks_created_at", "created_at"),
        Index("ix_tasks_updated_at", "updated_at"),
        CheckConstraint("length(title) > 0", name="ck_tasks_title_non_empty"),
    )
