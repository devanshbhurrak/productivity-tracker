from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
import uuid
from app.schemas.time_session import TimeSessionResponse


class DashboardTodayResponse(BaseModel):
    date: date
    timezone: str
    tasks_worked_on: int
    tasks_worked_on_ids: List[uuid.UUID]
    total_tracked_seconds: int
    completed_count: int
    in_progress_count: int
    pending_count: int
    active_timer: Optional[TimeSessionResponse] = None
