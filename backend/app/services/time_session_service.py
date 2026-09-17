from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
import uuid

from app.repositories.time_session_repository import TimeSessionRepository
from app.repositories.task_repository import TaskRepository
from app.models.time_session import TimeSession
from app.models.task import TaskStatus
from app.exceptions.base import NotFoundException, ConflictException, BadRequestException, ForbiddenException


class TimeSessionService:
    def __init__(self, db: Session):
        self.db = db
        self.session_repo = TimeSessionRepository(db)
        self.task_repo = TaskRepository(db)

    def start_timer(self, user_id: uuid.UUID, task_id: uuid.UUID) -> TimeSession:
        # Verify task exists and belongs to user
        task = self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            raise NotFoundException(code="TASK_NOT_FOUND", message="Task not found")

        # Check that user does not already have active timer
        active = self.session_repo.get_active_for_user(user_id)
        if active:
            raise ConflictException(code="ACTIVE_TIMER_EXISTS", message="Another task is already being tracked.")

        # Use transaction to atomically create session and possibly update task status
        try:
            # For SQLite, we need to handle transaction manually
            # Start a nested transaction if needed
            now = datetime.now(timezone.utc)
            session = self.session_repo.create_active(user_id=user_id, task_id=task_id, started_at=now)

            # If task is PENDING, transition to IN_PROGRESS
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.IN_PROGRESS
                task.updated_at = now
                self.db.add(task)

            self.db.commit()
            self.db.refresh(session)
            return session
        except IntegrityError as e:
            self.db.rollback()
            # This could be due to partial unique index violation in postgres concurrent case
            # Check if active exists again
            active = self.session_repo.get_active_for_user(user_id)
            if active:
                raise ConflictException(code="ACTIVE_TIMER_EXISTS", message="Another task is already being tracked.")
            raise ConflictException(code="CONFLICT", message="Could not start timer due to conflict")
        except ConflictException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise e

    def stop_timer(self, user_id: uuid.UUID, session_id: uuid.UUID) -> TimeSession:
        # Use FOR UPDATE to protect concurrent stop
        sess = self.session_repo.get_by_id(session_id, for_update=True)
        if not sess:
            raise NotFoundException(code="SESSION_NOT_FOUND", message="Time session not found")
        # Ensure aware comparison for SQLite naive
        sess_user = sess.user_id
        # Compare as string to handle UUID type differences
        if str(sess_user) != str(user_id):
            raise NotFoundException(code="SESSION_NOT_FOUND", message="Time session not found")
        if sess.ended_at is not None:
            raise ConflictException(code="SESSION_ALREADY_STOPPED", message="Session already stopped")

        try:
            now = datetime.now(timezone.utc)
            # Verify atomicity: reloading with lock would be ideal for postgres SELECT FOR UPDATE
            # For simplicity, check again and update
            updated = self.session_repo.stop_session(sess, now)
            self.db.commit()
            self.db.refresh(updated)
            return updated
        except ConflictException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise e

    def get_active(self, user_id: uuid.UUID) -> TimeSession | None:
        return self.session_repo.get_active_for_user(user_id)

    def list_sessions(self, user_id: uuid.UUID, **kwargs):
        return self.session_repo.list_sessions(user_id=user_id, **kwargs)

    def list_for_task(self, user_id: uuid.UUID, task_id: uuid.UUID, page: int, page_size: int):
        # Verify ownership
        task = self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            raise NotFoundException(code="TASK_NOT_FOUND", message="Task not found")
        return self.session_repo.get_sessions_for_task(task_id, user_id, page, page_size)

    def get_time_summary(self, user_id: uuid.UUID, task_id: uuid.UUID) -> dict:
        task = self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            raise NotFoundException(code="TASK_NOT_FOUND", message="Task not found")
        total = self.task_repo.get_total_tracked_seconds(task_id, user_id)
        # Count sessions
        from sqlalchemy import func
        from app.models.time_session import TimeSession
        count = self.db.query(func.count(TimeSession.id)).filter(
            TimeSession.task_id == task_id, TimeSession.user_id == user_id
        ).scalar() or 0
        return {"task_id": task_id, "total_tracked_seconds": int(total), "session_count": int(count)}
