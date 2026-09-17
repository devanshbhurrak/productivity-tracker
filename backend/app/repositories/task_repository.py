from sqlalchemy.orm import Session
from sqlalchemy import func, or_, asc, desc
from typing import Optional, List, Tuple
import uuid
from app.models.task import Task, TaskStatus
from app.models.time_session import TimeSession


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: uuid.UUID, title: str, description: Optional[str], status: TaskStatus) -> Task:
        task = Task(user_id=user_id, title=title, description=description, status=status)
        # Handle completed_at if status is COMPLETED
        if status == TaskStatus.COMPLETED:
            from datetime import datetime, timezone
            task.completed_at = datetime.now(timezone.utc)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_by_id_and_user(self, task_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Task]:
        return self.db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()

    def delete(self, task: Task):
        self.db.delete(task)
        self.db.commit()

    def update(self, task: Task, **kwargs) -> Task:
        for k, v in kwargs.items():
            setattr(task, k, v)
        self.db.commit()
        self.db.refresh(task)
        return task

    def list_tasks(
        self,
        user_id: uuid.UUID,
        page: int,
        page_size: int,
        search: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        created_from: Optional[str] = None,
        created_to: Optional[str] = None,
        updated_from: Optional[str] = None,
        updated_to: Optional[str] = None,
    ) -> Tuple[List[Task], int]:
        query = self.db.query(Task).filter(Task.user_id == user_id)

        if search:
            like = f"%{search}%"
            # For sqlite, ilike not available, use like lower; for postgres ilike works
            # Use ilike which sqlalchemy will translate appropriately
            query = query.filter(or_(Task.title.ilike(like), Task.description.ilike(like)))

        if status:
            query = query.filter(Task.status == status)

        # Date filters: parse ISO strings if provided
        from datetime import datetime
        def parse_dt(val: str):
            try:
                # Handle date-only like "2024-01-01"
                if "T" not in val and len(val) == 10:
                    return datetime.fromisoformat(val)
                return datetime.fromisoformat(val.replace("Z", "+00:00"))
            except Exception:
                return None

        if created_from:
            dt = parse_dt(created_from)
            if dt:
                query = query.filter(Task.created_at >= dt)
        if created_to:
            dt = parse_dt(created_to)
            if dt:
                query = query.filter(Task.created_at <= dt)
        if updated_from:
            dt = parse_dt(updated_from)
            if dt:
                query = query.filter(Task.updated_at >= dt)
        if updated_to:
            dt = parse_dt(updated_to)
            if dt:
                query = query.filter(Task.updated_at <= dt)

        total = query.count()

        # Whitelisted sort
        allowed_sort = {
            "created_at": Task.created_at,
            "updated_at": Task.updated_at,
            "title": Task.title,
            "completed_at": Task.completed_at,
            "status": Task.status,
        }
        sort_col = allowed_sort.get(sort_by, Task.created_at)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(desc(sort_col))

        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()
        return items, total

    def count_by_status(self, user_id: uuid.UUID) -> dict:
        # Returns dict status -> count
        rows = self.db.query(Task.status, func.count(Task.id)).filter(Task.user_id == user_id).group_by(Task.status).all()
        result = {s.value: 0 for s in TaskStatus}
        result.update({r[0].value if isinstance(r[0], TaskStatus) else str(r[0]): r[1] for r in rows})
        return result

    def get_total_tracked_seconds(self, task_id: uuid.UUID, user_id: uuid.UUID) -> int:
        # Sum durations for completed sessions
        total = self.db.query(func.coalesce(func.sum(TimeSession.duration), 0)).filter(
            TimeSession.task_id == task_id, TimeSession.user_id == user_id, TimeSession.duration.isnot(None)
        ).scalar()
        return int(total or 0)

    def get_active_session_id(self, task_id: uuid.UUID, user_id: uuid.UUID) -> Optional[uuid.UUID]:
        sess = self.db.query(TimeSession.id).filter(
            TimeSession.task_id == task_id, TimeSession.user_id == user_id, TimeSession.ended_at.is_(None)
        ).first()
        return sess[0] if sess else None

    def bulk_total_tracked(self, task_ids: List[uuid.UUID], user_id: uuid.UUID) -> dict:
        if not task_ids:
            return {}
        rows = self.db.query(TimeSession.task_id, func.coalesce(func.sum(TimeSession.duration), 0)).filter(
            TimeSession.user_id == user_id, TimeSession.task_id.in_(task_ids), TimeSession.duration.isnot(None)
        ).group_by(TimeSession.task_id).all()
        return {r[0]: int(r[1]) for r in rows}

    def bulk_active_sessions(self, task_ids: List[uuid.UUID], user_id: uuid.UUID) -> dict:
        if not task_ids:
            return {}
        rows = self.db.query(TimeSession.task_id, TimeSession.id).filter(
            TimeSession.user_id == user_id, TimeSession.task_id.in_(task_ids), TimeSession.ended_at.is_(None)
        ).all()
        return {r[0]: r[1] for r in rows}
