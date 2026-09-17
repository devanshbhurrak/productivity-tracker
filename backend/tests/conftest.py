import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Set test env before importing app
os.environ["APP_ENV"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["AUTH_SECRET"] = "test-secret-for-unit-tests-32chars!!"

from app.core.config import get_settings

# Clear cache
get_settings.cache_clear()
settings = get_settings()

# Now import app components
from app.core.database import Base, get_db
from app.main import app as fastapi_app
from app.models.user import User
from app.models.task import Task
from app.models.time_session import TimeSession
from app.core.security import _revoked_tokens

# Create test engine
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import models for create_all
import app.models.user  # noqa
import app.models.task  # noqa
import app.models.time_session  # noqa


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    # Ensure tables are clean
    try:
        Base.metadata.drop_all(bind=engine)
    except Exception:
        pass
    Base.metadata.create_all(bind=engine)
    # Create partial index
    with engine.connect() as conn:
        conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_time_sessions_one_active_per_user ON time_sessions (user_id) WHERE ended_at IS NULL"))
        conn.commit()
    yield
    try:
        Base.metadata.drop_all(bind=engine)
    except Exception:
        pass
    # Dispose engine before removing file on Windows
    try:
        engine.dispose()
    except Exception:
        pass
    try:
        if os.path.exists("./test.db"):
            os.remove("./test.db")
    except PermissionError:
        pass
    except FileNotFoundError:
        pass


@pytest.fixture(autouse=True)
def clear_db():
    # Clear data before each test and revoked tokens
    _revoked_tokens.clear()
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM time_sessions"))
        conn.execute(text("DELETE FROM tasks"))
        conn.execute(text("DELETE FROM users"))
        conn.commit()
    yield
    _revoked_tokens.clear()
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM time_sessions"))
        conn.execute(text("DELETE FROM tasks"))
        conn.execute(text("DELETE FROM users"))
        conn.commit()


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def user_factory(client):
    def _create(name="Test User", email=None, password="password123", timezone="UTC"):
        import uuid
        if email is None:
            email = f"user_{uuid.uuid4().hex[:8]}@example.com"
        r = client.post("/api/v1/auth/register", json={"name": name, "email": email, "password": password, "timezone": timezone})
        assert r.status_code == 201, r.text
        r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert r.status_code == 200, r.text
        token = r.json()["access_token"]
        user = r.json()["user"]
        return {"user": user, "token": token, "headers": {"Authorization": f"Bearer {token}"}, "email": email, "password": password}
    return _create


@pytest.fixture
def alice(user_factory):
    return user_factory(name="Alice", email="alice@example.com")

@pytest.fixture
def bob(user_factory):
    return user_factory(name="Bob", email="bob@example.com")
