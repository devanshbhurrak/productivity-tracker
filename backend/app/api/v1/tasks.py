from fastapi import APIRouter, Depends, Query, Response, status, Path
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.task import TaskCreateRequest, TaskUpdateRequest, TaskResponse, TaskStatus, TaskTimeSummaryResponse
from app.services.task_service import TaskService
from app.services.time_session_service import TimeSessionService
from app.schemas.time_session import TimeSessionResponse
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.utils.pagination import build_pagination_meta

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _to_task_response(task, total_tracked_seconds: int = 0, active_time_session_id=None) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        status=task.status.value if hasattr(task.status, "value") else str(task.status),
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
        total_tracked_seconds=total_tracked_seconds,
        active_time_session_id=active_time_session_id,
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TaskService(db)
    # Map schema status to model status
    from app.models.task import TaskStatus as ModelStatus
    status_enum = ModelStatus(payload.status.value) if payload.status else ModelStatus.PENDING
    task = service.create_task(
        user_id=current_user.id, title=payload.title, description=payload.description, status=status_enum
    )
    return _to_task_response(task, total_tracked_seconds=0, active_time_session_id=None)


@router.get("", response_model=dict)
def list_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search title/description"),
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    sort_by: str = Query("created_at", description="Sort field: created_at, updated_at, title, completed_at, status"),
    sort_order: str = Query("desc", description="Sort order: asc or desc", pattern="^(asc|desc)$"),
    created_from: Optional[str] = Query(None, description="Filter created_at >= ISO date"),
    created_to: Optional[str] = Query(None, description="Filter created_at <= ISO date"),
    updated_from: Optional[str] = Query(None, description="Filter updated_at >= ISO date"),
    updated_to: Optional[str] = Query(None, description="Filter updated_at <= ISO date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TaskService(db)
    from app.models.task import TaskStatus as ModelStatus
    status_filter = ModelStatus(status.value) if status else None
    # Validate sort_by whitelist
    allowed = {"created_at", "updated_at", "title", "completed_at", "status"}
    if sort_by not in allowed:
        sort_by = "created_at"
    items, total = service.list_tasks(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        search=search,
        status=status_filter,
        sort_by=sort_by,
        sort_order=sort_order,
        created_from=created_from,
        created_to=created_to,
        updated_from=updated_from,
        updated_to=updated_to,
    )
    enriched = service.enrich_tasks(items, current_user.id)
    resp_items = [_to_task_response(e["task"], e["total_tracked_seconds"], e["active_time_session_id"]) for e in enriched]
    pagination = build_pagination_meta(page, page_size, total)
    return {"items": [r.model_dump() for r in resp_items], "pagination": pagination}


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: uuid.UUID = Path(..., description="Task ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TaskService(db)
    data = service.get_task_with_aggregates(task_id, current_user.id)
    task = data["task"]
    return _to_task_response(task, data["total_tracked_seconds"], data["active_time_session_id"])


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    payload: TaskUpdateRequest,
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TaskService(db)
    from app.models.task import TaskStatus as ModelStatus
    status_val = ModelStatus(payload.status.value) if payload.status else None
    task = service.update_task(task_id=task_id, user_id=current_user.id, title=payload.title, description=payload.description, status=status_val)
    # Return with aggregates
    data = service.get_task_with_aggregates(task.id, current_user.id)
    return _to_task_response(data["task"], data["total_tracked_seconds"], data["active_time_session_id"])


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TaskService(db)
    service.delete_task(task_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Time sessions nested under tasks: keep here for route grouping
@router.get("/{task_id}/time-sessions", response_model=dict)
def get_task_time_sessions(
    task_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TimeSessionService(db)
    items, total = service.list_for_task(current_user.id, task_id, page, page_size)
    pagination = build_pagination_meta(page, page_size, total)
    return {"items": [TimeSessionResponse.model_validate(i).model_dump(mode="json") for i in items], "pagination": pagination}


@router.get("/{task_id}/time-summary", response_model=TaskTimeSummaryResponse)
def get_task_time_summary(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TimeSessionService(db)
    summary = service.get_time_summary(current_user.id, task_id)
    return summary
