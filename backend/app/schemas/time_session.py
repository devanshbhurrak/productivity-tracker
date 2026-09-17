from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
import uuid


class StartTimerRequest(BaseModel):
    task_id: uuid.UUID = Field(..., description="Task to start tracking")


class TimeSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    task_id: uuid.UUID
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration: Optional[int] = None
    created_at: datetime


class ActiveTimerResponse(BaseModel):
    active_session: Optional[TimeSessionResponse] = None
