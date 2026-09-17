from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc
from typing import Optional, List, Tuple
import uuid
from datetime import datetime, timezone
from app.models.time_session import TimeSession


class TimeSessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, session_id: uuid.UUID, for_update: bool = False) -> Optional[TimeSession]:
        q = self.db.query(TimeSession).filter(TimeSession.id == session_id)
        if for_update:
            try:
                q = q.with_for_update()
            except Exception:
                pass
        return q.first()

    def get_by_id_and_user(self, session_id: uuid.UUID, user_id: uuid.UUID) -> Optional[TimeSession]:
        return self.db.query(TimeSession).filter(TimeSession.id == session_id, TimeSession.user_id == user_id).first()

    def get_active_for_user(self, user_id: uuid.UUID) -> Optional[TimeSession]:
        return self.db.query(TimeSession).filter(TimeSession.user_id == user_id, TimeSession.ended_at.is_(None)).first()

    def create_active(self, user_id: uuid.UUID, task_id: uuid.UUID, started_at: datetime) -> TimeSession:
        sess = TimeSession(user_id=user_id, task_id=task_id, started_at=started_at, ended_at=None, duration=None)
        self.db.add(sess)
        self.db.flush()  # to get id, but not commit yet; caller handles transaction
        return sess

    @staticmethod
    def _ensure_aware(dt: datetime | None) -> datetime | None:
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    def stop_session(self, session: TimeSession, ended_at: datetime) -> TimeSession:
        started = self._ensure_aware(session.started_at)
        ended = self._ensure_aware(ended_at)
        duration = int((ended - started).total_seconds())
        if duration < 0:
            duration = 0
        session.ended_at = ended_at
        session.duration = duration
        self.db.flush()
        return session

    def list_sessions(
        self,
        user_id: uuid.UUID,
        page: int,
        page_size: int,
        task_id: Optional[uuid.UUID] = None,
        date_filter: Optional[str] = None,
        from_dt: Optional[str] = None,
        to_dt: Optional[str] = None,
        sort_by: str = "started_at",
        sort_order: str = "desc",
    ) -> Tuple[List[TimeSession], int]:
        query = self.db.query(TimeSession).filter(TimeSession.user_id == user_id)
        if task_id:
            query = query.filter(TimeSession.task_id == task_id)

        # Date filtering: from, to as ISO datetime strings
        def parse_dt(val: str):
            try:
                if "T" not in val and len(val) == 10:
                    from datetime import time, date
                    d = date.fromisoformat(val)
                    return datetime.combine(d, datetime.min.time()).replace(tzinfo=timezone.utc)
                return datetime.fromisoformat(val.replace("Z", "+00:00"))
            except Exception:
                return None

        if from_dt:
            dt = parse_dt(from_dt)
            if dt:
                query = query.filter(TimeSession.started_at >= dt)
        if to_dt:
            dt = parse_dt(to_dt)
            if dt:
                query = query.filter(TimeSession.started_at <= dt)
        if date_filter:
            # date_filter as YYYY-MM-DD, filter sessions where started_at date = that day (UTC)
            # For simplicity, treat as UTC day
            try:
                from datetime import date, time
                d = date.fromisoformat(date_filter)
                start = datetime.combine(d, time.min).replace(tzinfo=timezone.utc)
                end = datetime.combine(d, time.max).replace(tzinfo=timezone.utc)
                query = query.filter(TimeSession.started_at >= start, TimeSession.started_at <= end)
            except Exception:
                pass

        total = query.count()

        allowed_sort = {
            "started_at": TimeSession.started_at,
            "ended_at": TimeSession.ended_at,
            "created_at": TimeSession.created_at,
            "duration": TimeSession.duration,
        }
        sort_col = allowed_sort.get(sort_by, TimeSession.started_at)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(desc(sort_col))

        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()
        return items, total

    def get_sessions_for_task(self, task_id: uuid.UUID, user_id: uuid.UUID, page: int, page_size: int) -> Tuple[List[TimeSession], int]:
        query = self.db.query(TimeSession).filter(TimeSession.task_id == task_id, TimeSession.user_id == user_id)
        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(desc(TimeSession.started_at)).offset(offset).limit(page_size).all()
        return items, total

    def sum_duration_for_user(self, user_id: uuid.UUID) -> int:
        total = self.db.query(func.coalesce(func.sum(TimeSession.duration), 0)).filter(
            TimeSession.user_id == user_id, TimeSession.duration.isnot(None)
        ).scalar()
        return int(total or 0)

    def get_all_sessions_for_user(self, user_id: uuid.UUID) -> List[TimeSession]:
        return self.db.query(TimeSession).filter(TimeSession.user_id == user_id).all()

    def get_sessions_overlapping_day(self, user_id: uuid.UUID, day_start_utc: datetime, day_end_utc: datetime) -> List[TimeSession]:
        """
        Return sessions overlapping day, including active ones (ended_at is None)
        Logic: started_at <= day_end AND (ended_at IS NULL OR ended_at >= day_start)
        """
        # For active, treat ended_at as now
        now = datetime.now(timezone.utc)
        # We need to fetch all potentially overlapping
        query = self.db.query(TimeSession).filter(
            TimeSession.user_id == user_id,
            TimeSession.started_at <= day_end_utc,
        )
        # Need to handle ended_at null vs not null: (ended_at is None OR ended_at >= day_start)
        # Do in python for simplicity due to SQLite handling? But we can use SQL
        from sqlalchemy import or_
        query = query.filter(or_(TimeSession.ended_at.is_(None), TimeSession.ended_at >= day_start_utc))
        return query.all()
