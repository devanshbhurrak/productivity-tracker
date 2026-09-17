# Task and Time Tracking Backend — V1

Production-ready FastAPI + PostgreSQL backend for the Task and Time Tracking App (PRD V1).

## Features
- Secure authentication (register/login/logout/me) with bcrypt + JWT HttpOnly cookies
- User isolation on every endpoint (ownership checked at DB query level)
- Task CRUD, status management (PENDING→IN_PROGRESS→COMPLETED, reopen allowed), search/filter/sort/pagination
- Time tracking: start/stop timer, one active timer per user (enforced by DB partial unique index + app logic), server-side duration, concurrency protection
- Time sessions: list, filter, pagination, task time-summary, active timer
- Daily dashboard: tasks worked on today, total tracked seconds (midnight-crossing split), status counts, active timer, timezone-aware
- Validation, consistent error format, correct HTTP status codes, DB integrity, transactions, indexes, Alembic migrations, tests, OpenAPI docs

## Quick Start

### 1. Requirements
- Python 3.11+
- PostgreSQL 14+ (or SQLite for dev/test)

### 2. Setup
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment
Copy example and edit:
```bash
copy .env.example .env   # Windows
# cp .env.example .env   # Linux/Mac
```
Required vars (see `.env.example`):
```
APP_ENV=development
DATABASE_URL=postgresql://user:password@localhost:5432/productivity_tracker
# For local dev without Postgres:
# DATABASE_URL=sqlite:///./productivity_tracker.db
AUTH_SECRET=change-this-to-a-strong-random-secret-at-least-32-chars
FRONTEND_URL=http://localhost:3000
COOKIE_SECURE=false
```

### 4. Database
```bash
# Create database in Postgres first: createdb productivity_tracker
alembic upgrade head
# For SQLite dev, tables auto-create on startup, but migration still works
```

### 5. Run
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Health: `GET http://localhost:8000/health`
- Docs: `http://localhost:8000/docs` and `/redoc`
- API: `http://localhost:8000/api/v1/...`

### 6. Test

Uses isolated SQLite test DB (`./test.db`):
```bash
pytest tests/ -v
# or with coverage
pytest --tb=short
```
Test categories:
- `test_auth.py` — register, login, logout, validation, protected routes
- `test_authorization.py` — cross-user isolation for tasks/sessions/dashboard
- `test_tasks.py` — CRUD, status, search/filter/sort/pagination, validation
- `test_time_tracking.py` — start/stop, active, duplicates, concurrency, aggregation
- `test_dashboard.py` — daily summary, midnight crossing, timezone
- `test_health.py` — health and OpenAPI

## API Surface

### Auth
```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
```

### Tasks
```
POST   /api/v1/tasks
GET    /api/v1/tasks?search=&status=&sort_by=&sort_order=&page=&page_size=&created_from=&created_to=
GET    /api/v1/tasks/{task_id}
PATCH  /api/v1/tasks/{task_id}
DELETE /api/v1/tasks/{task_id}
GET    /api/v1/tasks/{task_id}/time-sessions
GET    /api/v1/tasks/{task_id}/time-summary
```

### Time Sessions
```
POST   /api/v1/time-sessions/start
POST   /api/v1/time-sessions/{session_id}/stop
GET    /api/v1/time-sessions?task_id=&date=&from=&to=&sort=&page=&page_size=
GET    /api/v1/time-sessions/active
```

### Dashboard
```
GET    /api/v1/dashboard/today
```

### System
```
GET    /health
GET    /docs
```

## Auth Details
- Passwords: bcrypt via passlib, never returned/logged
- JWT: HS256, 7-day expiry, `sub` = user_id
- Cookie: HttpOnly, Lax, Secure in production, 7-day max_age
- Header fallback: `Authorization: Bearer <token>` (takes precedence over cookie)
- Logout: revokes token (in-memory blocklist) + deletes cookie

## Data Model
- **User**: id (UUID), name, email (unique, normalized lowercase), password_hash, timezone, created_at, updated_at
- **Task**: id, user_id (FK cascade), title, description, status (enum), created_at, updated_at, completed_at
- **TimeSession**: id, user_id (FK), task_id (FK cascade), started_at (UTC), ended_at (nullable), duration (int seconds, nullable for active), created_at

Indexes: users.email, tasks.user_id/status/created/updated, time_sessions.user_id/task_id/started/ended + partial unique `WHERE ended_at IS NULL` for one-active-per-user.

## Pagination
```json
{
  "items": [],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 47,
    "total_pages": 3,
    "has_next": true,
    "has_previous": false
  }
}
```

## Error Format
```json
{
  "error": {
    "code": "ACTIVE_TIMER_EXISTS",
    "message": "Another task is already being tracked."
  }
}
```
Validation errors include `details.fields`.

## Security Notes
- Ownership filtered at DB query level, not in memory
- CORS explicitly configured via `FRONTEND_URL` / `CORS_ORIGINS`, no wildcard with credentials in production
- No stack traces or secrets in production errors
- All timestamps UTC, daily reporting converts local day boundaries to UTC

## Deployment
- Set `APP_ENV=production`, `COOKIE_SECURE=true`, strong `AUTH_SECRET`, real `DATABASE_URL`, `FRONTEND_URL`
- Run `alembic upgrade head` on deploy
- Use `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4`
- Health check: `/health`

## Project Structure
See `PRD.md — Task and Time Tracking App V1.md` section 69 for recommended layout. Current layout matches with additional `tests/` and `alembic/versions`.

## License
Internal project.
