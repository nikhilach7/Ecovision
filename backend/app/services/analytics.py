from datetime import datetime, timedelta, timezone


def clamp_fill_percentage(distance_cm: float, max_depth_cm: float) -> float:
    ratio = 1 - (distance_cm / max_depth_cm)
    return round(max(0.0, min(1.0, ratio)) * 100, 2)


def day_bounds(target: datetime | None = None) -> tuple[datetime, datetime]:
    dt = target or datetime.now(timezone.utc)
    start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return start, end
