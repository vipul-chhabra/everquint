from datetime import datetime, timezone
from urllib.parse import quote


def utc(year, month, day, hour=0, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)


def iso(dt):
    return dt.isoformat()


def qdt(dt):
    return quote(dt.isoformat())