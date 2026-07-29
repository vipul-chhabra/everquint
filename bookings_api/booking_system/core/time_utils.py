
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from core.exceptions import InvalidTimezoneException


def resolve_timezone(tz_name):
    try:
        return ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, ValueError, KeyError):
        raise InvalidTimezoneException("Unknown timezone: '{0}'.".format(tz_name))


def intervals_overlap(start_a, end_a, start_b, end_b):
    return start_a < end_b and start_b < end_a


def overlap_hours(start_a, end_a, start_b, end_b):
    latest_start = max(start_a, start_b)
    earliest_end = min(end_a, end_b)
    seconds = (earliest_end - latest_start).total_seconds()
    return max(0.0, seconds) / 3600.0
