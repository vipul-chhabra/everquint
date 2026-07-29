
from django.utils import timezone
from django.utils.dateparse import parse_datetime as dj_parse_datetime

from core.exceptions import InvalidQueryParameterException


def parse_int(raw, field):
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise InvalidQueryParameterException('{0} must be an integer.'.format(field))


def parse_datetime(raw, field):
    if raw is None:
        return None
    try:
        parsed = dj_parse_datetime(raw)
    except ValueError:
        parsed = None
    if parsed is None:
        raise InvalidQueryParameterException('{0} must be a valid ISO-8601 datetime.'.format(field))
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed
