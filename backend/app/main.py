import logging as _logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings

_startup_logger = _logging.getLogger(__name__)
from app.core.database import create_all_tables, Base, engine
from app.api.router import api_router
from app.exceptions.handlers import register_exception_handlers
from app.core.logging import logging_middleware

settings = get_settings()

app = FastAPI(
    title="Task and Time Tracking API",
    version="1.0.0",
    description="Production-ready Task and Time Tracking backend per PRD V1",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS
origins = settings.allowed_origins
# In production, wildcard not allowed with credentials; ensure explicit origins
if settings.is_production and "*" in origins:
    origins = [o for o in origins if o != "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging middleware
@app.middleware("http")
async def log_middleware(request: Request, call_next):
    return await logging_middleware(request, call_next)

# Exception handlers
register_exception_handlers(app)

# Include API router
app.include_router(api_router)


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "version": "1.0.0", "env": settings.app_env}


@app.get("/", tags=["system"])
def root():
    return {"message": "Task and Time Tracking API", "docs": "/docs", "health": "/health"}


# Create tables on startup if not in production with migrations?
# For dev and testing, ensure tables exist
@app.on_event("startup")
def on_startup():
    # Only auto-create for sqlite or testing; in production rely on alembic
    db_url = settings.get_database_url()
    if db_url.startswith("sqlite") or settings.is_testing:
        try:
            create_all_tables()
        except Exception as e:
            _startup_logger.warning("create_all_tables failed (tables may already exist): %s", e)
        # Create partial unique index for SQLite if needed via raw SQL for active timer enforcement?
        # SQLite does not support partial indexes via SQLAlchemy create_all, we create manually
        try:
            from sqlalchemy import text
            with engine.connect() as conn:
                # Create unique index for one active per user where ended_at IS NULL
                # SQLite supports WHERE clause in CREATE UNIQUE INDEX since 3.8.0
                conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_time_sessions_one_active_per_user ON time_sessions (user_id) WHERE ended_at IS NULL"))
                conn.commit()
        except Exception as e:
            _startup_logger.warning("Could not create partial unique index (may already exist or DB unsupported): %s", e)
