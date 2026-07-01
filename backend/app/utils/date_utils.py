# ============================================================
# Utility — Date Helpers
# ============================================================

from datetime import date, datetime, timedelta, timezone


def utc_now() -> datetime:
    """Current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


def today_utc() -> date:
    """Current UTC date."""
    return utc_now().date()


def start_of_week(d: date | None = None) -> date:
    """Monday of the week containing `d` (defaults to today)."""
    d = d or today_utc()
    return d - timedelta(days=d.weekday())


def end_of_week(d: date | None = None) -> date:
    """Sunday of the week containing `d` (defaults to today)."""
    return start_of_week(d) + timedelta(days=6)


def start_of_month(d: date | None = None) -> date:
    """First day of the month containing `d`."""
    d = d or today_utc()
    return d.replace(day=1)


def end_of_month(d: date | None = None) -> date:
    """Last day of the month containing `d`."""
    d = d or today_utc()
    if d.month == 12:
        return d.replace(day=31)
    return d.replace(month=d.month + 1, day=1) - timedelta(days=1)


def days_between(start: date, end: date) -> int:
    """Number of days between two dates (inclusive)."""
    return (end - start).days + 1


def date_range(start: date, end: date) -> list[date]:
    """List of dates from start to end (inclusive)."""
    return [start + timedelta(days=i) for i in range(days_between(start, end))]
