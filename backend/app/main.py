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
# For dev and testing, ensure tables exist. In production (Postgres) rely on Alembic,
# but also self-heal if tables were previously auto-created without stamping.
@app.on_event("startup")
def on_startup():
    db_url = settings.get_database_url()
    if db_url.startswith("sqlite") or settings.is_testing:
        try:
            create_all_tables()
        except Exception as e:
            _startup_logger.warning("create_all_tables failed (tables may already exist): %s", e)
        # SQLite does not support partial indexes via SQLAlchemy create_all, we create manually
        try:
            from sqlalchemy import text

            with engine.connect() as conn:
                # One active timer per user where ended_at IS NULL (supported since SQLite 3.8.0)
                conn.execute(
                    text(
                        "CREATE UNIQUE INDEX IF NOT EXISTS ix_time_sessions_one_active_per_user ON time_sessions (user_id) WHERE ended_at IS NULL"
                    )
                )
                conn.commit()
        except Exception as e:
            _startup_logger.warning(
                "Could not create partial unique index (may already exist or DB unsupported): %s", e
            )
    else:
        # Postgres / production: don't blindly create_all_tables (would conflict with Alembic).
        # Instead, ensure alembic_version is consistent:
        # - if tables don't exist yet (first Vercel deploy), create them and stamp head
        # - if tables exist but alembic_version is missing/empty, stamp head
        try:
            from sqlalchemy import inspect, text

            insp = inspect(engine)
            tables = insp.get_table_names()
            has_users = "users" in tables
            has_alembic = "alembic_version" in tables
            needs_create = not has_users
            needs_stamp = False

            if needs_create:
                _startup_logger.info("Postgres tables missing, creating via create_all_tables and stamping head")
                create_all_tables()
                # Ensure partial unique index for one active timer per user
                with engine.connect() as conn:
                    conn.execute(
                        text(
                            "CREATE UNIQUE INDEX IF NOT EXISTS ix_time_sessions_one_active_per_user ON time_sessions (user_id) WHERE ended_at IS NULL"
                        )
                    )
                    conn.commit()
                # re-inspect after creation
                tables = inspect(engine).get_table_names()
                has_alembic = "alembic_version" in tables
                needs_stamp = True
            elif not has_alembic:
                needs_stamp = True
            else:
                with engine.connect() as conn:
                    rows = conn.execute(text("SELECT version_num FROM alembic_version")).fetchall()
                    if not rows:
                        needs_stamp = True

            # Ensure partial index exists even for existing DBs (previous unconditional path missed it for Postgres)
            try:
                with engine.connect() as conn:
                    conn.execute(
                        text(
                            "CREATE UNIQUE INDEX IF NOT EXISTS ix_time_sessions_one_active_per_user ON time_sessions (user_id) WHERE ended_at IS NULL"
                        )
                    )
                    conn.commit()
            except Exception as idx_e:
                _startup_logger.warning("Could not ensure partial unique index for Postgres: %s", idx_e)

            if needs_stamp:
                _startup_logger.info("Stamping alembic_version to head (1b9d75d25200)")
                with engine.connect() as conn:
                    conn.execute(
                        text(
                            "CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))"
                        )
                    )
                    conn.execute(text("DELETE FROM alembic_version"))
                    conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('1b9d75d25200')"))
                    conn.commit()
        except Exception as e:
            _startup_logger.warning("Postgres startup check failed (non-fatal): %s", e)
