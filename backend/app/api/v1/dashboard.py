from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardTodayResponse
from app.schemas.task import TaskResponse
from app.schemas.time_session import TimeSessionResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _to_task_response(enriched: dict) -> TaskResponse:
    task = enriched["task"]
    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        status=task.status.value if hasattr(task.status, "value") else str(task.status),
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
        total_tracked_seconds=enriched["total_tracked_seconds"],
        active_time_session_id=enriched["active_time_session_id"],
    )


@router.get("/today", response_model=DashboardTodayResponse)
def get_today_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DashboardService(db)
    summary = service.get_today_summary(user_id=current_user.id, user_timezone=current_user.timezone)
    active = summary.pop("active_timer")
    active_resp = TimeSessionResponse.model_validate(active) if active else None
    tasks_worked_on = [_to_task_response(e) for e in summary["tasks_worked_on"]]
    return DashboardTodayResponse(
        date=summary["date"],
        timezone=summary["timezone"],
        tasks_worked_on=tasks_worked_on,
        total_tracked_seconds=summary["total_tracked_seconds"],
        completed_count=summary["completed_count"],
        in_progress_count=summary["in_progress_count"],
        pending_count=summary["pending_count"],
        active_timer=active_resp,
    )
