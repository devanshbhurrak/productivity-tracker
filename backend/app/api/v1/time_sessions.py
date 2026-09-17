from fastapi import APIRouter, Depends, Query, status, Path
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.time_session import StartTimerRequest, TimeSessionResponse
from app.services.time_session_service import TimeSessionService
from app.utils.pagination import build_pagination_meta
from app.exceptions.base import NotFoundException

router = APIRouter(prefix="/time-sessions", tags=["time-sessions"])


@router.post("/start", response_model=TimeSessionResponse, status_code=status.HTTP_201_CREATED)
def start_timer(
    payload: StartTimerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TimeSessionService(db)
    sess = service.start_timer(user_id=current_user.id, task_id=payload.task_id)
    return sess


@router.post("/{session_id}/stop", response_model=TimeSessionResponse)
def stop_timer(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TimeSessionService(db)
    sess = service.stop_timer(user_id=current_user.id, session_id=session_id)
    return sess


@router.get("/active", response_model=TimeSessionResponse)
def get_active_timer(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TimeSessionService(db)
    active = service.get_active(user_id=current_user.id)
    if not active:
        raise NotFoundException(code="NO_ACTIVE_TIMER", message="No active timer")
    return active


@router.get("", response_model=dict)
def list_time_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    task_id: Optional[uuid.UUID] = Query(None),
    date: Optional[str] = Query(None, description="Filter by date YYYY-MM-DD (UTC)"),
    from_date: Optional[str] = Query(None, alias="from", description="Filter started_at >= ISO"),
    to_date: Optional[str] = Query(None, alias="to", description="Filter started_at <= ISO"),
    sort_by: str = Query("started_at", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TimeSessionService(db)
    allowed_sort = {"started_at", "ended_at", "created_at", "duration"}
    if sort_by not in allowed_sort:
        sort_by = "started_at"
    items, total = service.list_sessions(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        task_id=task_id,
        date_filter=date,
        from_dt=from_date,
        to_dt=to_date,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    pagination = build_pagination_meta(page, page_size, total)
    return {"items": [TimeSessionResponse.model_validate(i).model_dump(mode="json") for i in items], "pagination": pagination}
