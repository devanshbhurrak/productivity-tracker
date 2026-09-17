from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardTodayResponse
from app.schemas.time_session import TimeSessionResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/today", response_model=DashboardTodayResponse)
def get_today_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DashboardService(db)
    summary = service.get_today_summary(user_id=current_user.id, user_timezone=current_user.timezone)
    # Convert active_timer to response schema if exists
    active = summary.pop("active_timer")
    active_resp = TimeSessionResponse.model_validate(active) if active else None
    return DashboardTodayResponse(
        date=summary["date"],
        timezone=summary["timezone"],
        tasks_worked_on=summary["tasks_worked_on"],
        tasks_worked_on_ids=summary["tasks_worked_on_ids"],
        total_tracked_seconds=summary["total_tracked_seconds"],
        completed_count=summary["completed_count"],
        in_progress_count=summary["in_progress_count"],
        pending_count=summary["pending_count"],
        active_timer=active_resp,
    )
