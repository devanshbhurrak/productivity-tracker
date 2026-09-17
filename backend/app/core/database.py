from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.core.config import get_settings

settings = get_settings()
DATABASE_URL = settings.get_database_url()

# For SQLite we need check_same_thread=False
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_tables():
    # Import models to register
    import app.models.user  # noqa: F401
    import app.models.task  # noqa: F401
    import app.models.time_session  # noqa: F401

    Base.metadata.create_all(bind=engine)
