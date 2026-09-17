# Productivity Tracker

A full-stack task and time tracking application. Log tasks, track time sessions, and view productivity dashboards.

## Tech Stack

**Backend** — FastAPI · PostgreSQL · SQLAlchemy · Alembic · JWT auth  
**Frontend** — React 18 · TypeScript · Vite · Tailwind CSS · TanStack Query

## Project Structure

```
productivity-tracker/
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── api/      # Route handlers
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   └── core/     # Config, DB, security
│   ├── alembic/      # Database migrations
│   └── tests/        # Pytest test suite
└── frontend/         # React application
    └── src/
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (or SQLite for local dev)

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database URL and secret key

# Run migrations
alembic upgrade head

# Start dev server
uvicorn app.main:app --reload --port 8000
```

API available at `http://localhost:8000`  
Docs at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

App available at `http://localhost:3000`

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | — |
| `AUTH_SECRET` | JWT signing secret (min 32 chars) | — |
| `FRONTEND_URL` | Allowed CORS origin | `http://localhost:3000` |
| `APP_ENV` | `development` or `production` | `development` |
| `COOKIE_SECURE` | Secure cookie flag | `false` |

## Running Tests

```bash
cd backend
pytest
```
