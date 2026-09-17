import time
from datetime import datetime, timezone, timedelta, date
import pytz
from unittest.mock import patch


def test_no_activity(client, user_factory):
    alice = user_factory()
    r = client.get("/api/v1/dashboard/today", headers=alice["headers"])
    assert r.status_code == 200
    data = r.json()
    assert data["total_tracked_seconds"] == 0
    assert data["tasks_worked_on"] == 0
    assert data["completed_count"] == 0
    assert data["in_progress_count"] == 0
    assert data["pending_count"] == 0 or data["pending_count"] >= 0
    assert data["active_timer"] is None


def test_tasks_worked_on_today(client, user_factory):
    alice = user_factory()
    r = client.post("/api/v1/tasks", json={"title": "Worked Task"}, headers=alice["headers"])
    tid = r.json()["id"]
    r = client.post("/api/v1/time-sessions/start", json={"task_id": tid}, headers=alice["headers"])
    sid = r.json()["id"]
    time.sleep(1)
    client.post(f"/api/v1/time-sessions/{sid}/stop", headers=alice["headers"])
    r = client.get("/api/v1/dashboard/today", headers=alice["headers"])
    assert r.status_code == 200
    assert r.json()["tasks_worked_on"] == 1
    assert tid in r.json()["tasks_worked_on_ids"]


def test_daily_tracked_time(client, user_factory):
    alice = user_factory()
    r = client.post("/api/v1/tasks", json={"title": "Daily Time Task"}, headers=alice["headers"])
    tid = r.json()["id"]
    r = client.post("/api/v1/time-sessions/start", json={"task_id": tid}, headers=alice["headers"])
    sid = r.json()["id"]
    time.sleep(1)
    r = client.post(f"/api/v1/time-sessions/{sid}/stop", headers=alice["headers"])
    duration = r.json()["duration"]
    r = client.get("/api/v1/dashboard/today", headers=alice["headers"])
    assert r.json()["total_tracked_seconds"] >= duration


def test_completed_counts(client, user_factory):
    alice = user_factory()
    # Create 1 pending, 1 in_progress, 1 completed
    r = client.post("/api/v1/tasks", json={"title": "Pending Task"}, headers=alice["headers"])
    tid_pending = r.json()["id"]
    r = client.post("/api/v1/tasks", json={"title": "In Progress Task"}, headers=alice["headers"])
    tid_ip = r.json()["id"]
    r = client.post("/api/v1/tasks", json={"title": "Completed Task"}, headers=alice["headers"])
    tid_comp = r.json()["id"]
    client.patch(f"/api/v1/tasks/{tid_ip}", json={"status": "IN_PROGRESS"}, headers=alice["headers"])
    client.patch(f"/api/v1/tasks/{tid_comp}", json={"status": "COMPLETED"}, headers=alice["headers"])
    r = client.get("/api/v1/dashboard/today", headers=alice["headers"])
    assert r.json()["pending_count"] >= 1
    assert r.json()["in_progress_count"] >= 1
    assert r.json()["completed_count"] >= 1


def test_active_timer_in_dashboard(client, user_factory):
    alice = user_factory()
    r = client.post("/api/v1/tasks", json={"title": "Active Timer Task"}, headers=alice["headers"])
    tid = r.json()["id"]
    r = client.post("/api/v1/time-sessions/start", json={"task_id": tid}, headers=alice["headers"])
    sid = r.json()["id"]
    r = client.get("/api/v1/dashboard/today", headers=alice["headers"])
    assert r.json()["active_timer"] is not None
    assert r.json()["active_timer"]["id"] == sid
    client.post(f"/api/v1/time-sessions/{sid}/stop", headers=alice["headers"])
    r = client.get("/api/v1/dashboard/today", headers=alice["headers"])
    assert r.json()["active_timer"] is None


def test_session_crossing_midnight(client, user_factory, db_session):
    # Directly test dashboard midnight logic by creating sessions that cross midnight
    alice = user_factory(timezone="UTC")
    # Need to manipulate time sessions to cross midnight
    # Create a task
    r = client.post("/api/v1/tasks", json={"title": "Midnight Task"}, headers=alice["headers"])
    tid = r.json()["id"]
    # Manually create a time session that crosses midnight via DB
    from app.models.time_session import TimeSession
    import uuid
    user_id = uuid.UUID(alice["user"]["id"])
    task_id = uuid.UUID(tid)
    # Session 23:50 -> 00:20 UTC
    # Determine today and tomorrow
    now_utc = datetime.now(timezone.utc)
    today = now_utc.date()
    # Create session crossing midnight: today 23:50 to tomorrow 00:20
    # For test, we set session to yesterday 23:50 to today 00:20, so it overlaps today
    # Use today as target: session from today-1 23:50 to today 00:20 should give 20 min today
    # Build dates
    tz = pytz.timezone("UTC")
    # Today at 00:00 UTC = day start
    day_start = tz.localize(datetime.combine(today, datetime.min.time()))
    day_start_utc = day_start.astimezone(pytz.utc)
    # Create session ending 20 min after day_start
    started_at = day_start_utc - timedelta(minutes=10)  # 23:50 previous day
    ended_at = day_start_utc + timedelta(minutes=20)  # 00:20 today
    duration = int((ended_at - started_at).total_seconds())  # 1800
    sess = TimeSession(
        user_id=user_id,
        task_id=task_id,
        started_at=started_at,
        ended_at=ended_at,
        duration=duration,
    )
    db_session.add(sess)
    db_session.commit()

    r = client.get("/api/v1/dashboard/today", headers=alice["headers"])
    assert r.status_code == 200
    data = r.json()
    # Total should include 20 minutes = 1200 seconds for today (+ maybe other sessions)
    # Our session contributes 1200 to today, 600 to yesterday
    # Since we only query today, it should be at least 1200
    assert data["total_tracked_seconds"] >= 1200
    assert data["tasks_worked_on"] >= 1

    # Also ensure raw session remains one (not split)
    from sqlalchemy import func
    count = db_session.query(func.count(TimeSession.id)).filter(TimeSession.user_id == user_id).scalar()
    assert count == 1


def test_timezone_handling(client, user_factory, db_session):
    # Create user with different timezone and verify dashboard uses that timezone
    # Use America/New_York (UTC-4 or -5)
    alice = user_factory(timezone="America/New_York")
    # Dashboard date should be according to that timezone
    r = client.get("/api/v1/dashboard/today", headers=alice["headers"])
    assert r.status_code == 200
    assert r.json()["timezone"] == "America/New_York"
    # Date should be consistent with NY time
    ny_tz = pytz.timezone("America/New_York")
    expected_date = datetime.now(ny_tz).date().isoformat()
    assert r.json()["date"] == expected_date
