from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
import uuid


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: str
    timezone: str
    created_at: datetime
    updated_at: datetime
