from datetime import datetime, timezone, timedelta, date, time
import pytz


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def get_day_boundaries_utc(user_tz: str, target_date: date | None = None) -> tuple[datetime, datetime]:
    """
    Given user's IANA timezone and target_date (local date), return (start_utc, end_utc)
    If target_date is None, use today in that timezone.
    """
    tz = pytz.timezone(user_tz)
    if target_date is None:
        now_local = datetime.now(tz)
        target_date = now_local.date()

    # Local day start 00:00:00
    local_start = tz.localize(datetime.combine(target_date, time.min))
    local_end = tz.localize(datetime.combine(target_date, time.max))  # 23:59:59.999999

    # Convert to UTC
    start_utc = local_start.astimezone(pytz.utc)
    end_utc = local_end.astimezone(pytz.utc)
    return start_utc, end_utc


def ensure_aware_utc(dt: datetime) -> datetime:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def calculate_overlap_seconds(session_start: datetime, session_end: datetime, day_start_utc: datetime, day_end_utc: datetime) -> int:
    """
    Calculate seconds overlapping between [session_start, session_end] and [day_start_utc, day_end_utc]
    All datetimes must be timezone-aware UTC.
    """
    session_start = ensure_aware_utc(session_start)
    session_end = ensure_aware_utc(session_end)
    day_start_utc = ensure_aware_utc(day_start_utc)
    day_end_utc = ensure_aware_utc(day_end_utc)

    latest_start = max(session_start, day_start_utc)
    earliest_end = min(session_end, day_end_utc)
    if latest_start >= earliest_end:
        return 0
    delta = earliest_end - latest_start
    return int(delta.total_seconds())
