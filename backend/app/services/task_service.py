from sqlalchemy.orm import Session
from typing import Optional
import uuid
from datetime import datetime, timezone

from app.repositories.task_repository import TaskRepository
from app.models.task import TaskStatus, Task
from app.exceptions.base import NotFoundException, BadRequestException


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TaskRepository(db)

    def create_task(self, user_id: uuid.UUID, title: str, description: Optional[str], status: TaskStatus = TaskStatus.PENDING) -> Task:
        return self.repo.create(user_id=user_id, title=title, description=description, status=status)

    def get_task(self, task_id: uuid.UUID, user_id: uuid.UUID) -> Task:
        task = self.repo.get_by_id_and_user(task_id, user_id)
        if not task:
            raise NotFoundException(code="TASK_NOT_FOUND", message="Task not found")
        return task

    def list_tasks(self, user_id: uuid.UUID, **kwargs):
        return self.repo.list_tasks(user_id=user_id, **kwargs)

    def update_task(self, task_id: uuid.UUID, user_id: uuid.UUID, title: Optional[str] = None, description: Optional[str] = None, status: Optional[TaskStatus] = None) -> Task:
        task = self.get_task(task_id, user_id)
        update_fields = {}

        if title is not None:
            update_fields["title"] = title
        if description is not None:
            # If explicitly passed as None, clear; else set
            update_fields["description"] = description
        # Handle status transition logic
        if status is not None:
            # Validate transition? Allow all but enforce consistency of completed_at
            # According spec: explicitly handle whether reopening completed is allowed - we allow it
            # Transition rules: any -> any is allowed in V1 but we log completed_at handling
            current = task.status
            new_status = status
            if current != new_status:
                if new_status == TaskStatus.COMPLETED:
                    update_fields["status"] = new_status
                    update_fields["completed_at"] = datetime.now(timezone.utc)
                else:
                    # Moving away from completed -> clear completed_at
                    update_fields["status"] = new_status
                    update_fields["completed_at"] = None
                    # If was COMPLETED and moving to PENDING/IN_PROGRESS, allowed
                # Also handle PENDING -> IN_PROGRESS etc: no extra logic
            # else same status, no change

        # If no status provided, keep existing
        if update_fields:
            task = self.repo.update(task, **update_fields)
        return task

    def delete_task(self, task_id: uuid.UUID, user_id: uuid.UUID):
        task = self.get_task(task_id, user_id)
        # Atomic deletion: due to cascade, associated time_sessions deleted
        # Use transaction
        try:
            self.repo.delete(task)
        except Exception as e:
            self.db.rollback()
            raise e

    def get_task_with_aggregates(self, task_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        task = self.get_task(task_id, user_id)
        total = self.repo.get_total_tracked_seconds(task_id, user_id)
        active_id = self.repo.get_active_session_id(task_id, user_id)
        return {"task": task, "total_tracked_seconds": total, "active_time_session_id": active_id}

    def enrich_tasks(self, tasks: list[Task], user_id: uuid.UUID) -> list[dict]:
        if not tasks:
            return []
        ids = [t.id for t in tasks]
        totals = self.repo.bulk_total_tracked(ids, user_id)
        actives = self.repo.bulk_active_sessions(ids, user_id)
        result = []
        for t in tasks:
            result.append({
                "task": t,
                "total_tracked_seconds": totals.get(t.id, 0),
                "active_time_session_id": actives.get(t.id)
            })
        return result
