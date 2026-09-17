from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.time_sessions import router as time_sessions_router
from app.api.v1.dashboard import router as dashboard_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(tasks_router)
api_router.include_router(time_sessions_router)
api_router.include_router(dashboard_router)
