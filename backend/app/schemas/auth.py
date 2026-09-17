from pydantic import BaseModel, EmailStr, Field, field_validator
import re
import pytz


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="User display name")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password min 8 chars")
    timezone: str = Field(default="UTC", max_length=50, description="IANA timezone")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty or whitespace")
        return v

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        if v not in pytz.all_timezones:
            raise ValueError(f"Invalid timezone: {v}")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        # Require at least one letter and one number or simple complexity
        # Keep validation simple as per PRD: minimum security requirements
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
