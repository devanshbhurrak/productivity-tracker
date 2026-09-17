import os
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_env: str = Field(default="development", alias="APP_ENV")
    database_url: str = Field(
        default="sqlite:///./productivity_tracker.db", alias="DATABASE_URL"
    )
    auth_secret: str = Field(default="dev-secret-change-in-production-32chars!!", alias="AUTH_SECRET")
    frontend_url: str = Field(default="http://localhost:3000", alias="FRONTEND_URL")
    cookie_secure: bool = Field(default=False, alias="COOKIE_SECURE")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    cookie_name: str = "access_token"
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def is_testing(self) -> bool:
        return self.app_env.lower() == "testing"

    @property
    def allowed_origins(self) -> List[str]:
        # FRONTEND_URL takes precedence, CORS_ORIGINS can be comma separated
        origins = []
        if self.frontend_url:
            origins.append(self.frontend_url)
        if self.cors_origins and self.cors_origins != self.frontend_url:
            for o in self.cors_origins.split(","):
                o = o.strip()
                if o and o not in origins:
                    origins.append(o)
        return origins

    def get_database_url(self) -> str:
        # Allow override via env
        url = os.getenv("DATABASE_URL", self.database_url)
        return url


@lru_cache()
def get_settings() -> Settings:
    return Settings()
