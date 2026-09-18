from sqlalchemy.orm import Session
from datetime import datetime, timezone, date
import uuid
import pytz
from sqlalchemy import func

from app.repositories.task_repository import TaskRepository
from app.repositories.time_session_repository import TimeSessionRepository
from app.models.task import TaskStatus
from app.models.time_session import TimeSession
from app.utils.datetime import get_day_boundaries_utc, calculate_overlap_seconds


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.session_repo = TimeSessionRepository(db)

    def get_today_summary(self, user_id: uuid.UUID, user_timezone: str) -> dict:
        # Determine today's boundaries in UTC
        today_local = datetime.now(pytz.timezone(user_timezone)).date()
        day_start_utc, day_end_utc = get_day_boundaries_utc(user_timezone, today_local)

        # Get status counts
        counts = self.task_repo.count_by_status(user_id)
        pending = counts.get("PENDING", 0)
        in_progress = counts.get("IN_PROGRESS", 0)
        completed = counts.get("COMPLETED", 0)

        # Get active timer
        active = self.session_repo.get_active_for_user(user_id)

        # Find tasks worked on today: tasks with at least one session overlapping today
        # And total tracked seconds today (with midnight splitting)
        overlapping_sessions = self.session_repo.get_sessions_overlapping_day(user_id, day_start_utc, day_end_utc)

        total_seconds_today = 0
        worked_task_ids = set()

        now_utc = datetime.now(timezone.utc)
        for sess in overlapping_sessions:
            # Determine effective end: if active, use now
            sess_end = sess.ended_at if sess.ended_at else now_utc
            overlap = calculate_overlap_seconds(sess.started_at, sess_end, day_start_utc, day_end_utc)
            if overlap > 0:
                total_seconds_today += overlap
                worked_task_ids.add(sess.task_id)

        # Fetch and enrich the tasks worked on today
        tasks_worked_on = []
        if worked_task_ids:
            from app.models.task import Task
            tasks = self.db.query(Task).filter(
                Task.id.in_(list(worked_task_ids)),
                Task.user_id == user_id,
            ).all()
            enriched = self.task_repo.bulk_total_tracked(list(worked_task_ids), user_id)
            actives = self.task_repo.bulk_active_sessions(list(worked_task_ids), user_id)
            for t in tasks:
                tasks_worked_on.append({
                    "task": t,
                    "total_tracked_seconds": enriched.get(t.id, 0),
                    "active_time_session_id": actives.get(t.id),
                })

        return {
            "date": today_local,
            "timezone": user_timezone,
            "tasks_worked_on": tasks_worked_on,
            "total_tracked_seconds": total_seconds_today,
            "completed_count": completed,
            "in_progress_count": in_progress,
            "pending_count": pending,
            "active_timer": active,
        }
