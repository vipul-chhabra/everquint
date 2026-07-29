
from datetime import datetime, time, timedelta

from booking.constants import  BUSINESS_WEEKDAYS, MAX_BOOKING_DURATION_HOURS, MIN_BOOKING_DURATION_MINUTES, MIN_DURATION, MAX_DURATION , \
    BUSINESS_START, BUSINESS_END
from booking.exceptions import InvalidBookingDurationException, InvalidTimeRangeException, OutsideBusinessHoursException
from core.time_utils import overlap_hours, resolve_timezone


def validate_time_order(start_time, end_time):
    if not start_time < end_time:
        raise InvalidTimeRangeException()


def validate_duration(start_time, end_time):
    duration = end_time - start_time
    if duration < MIN_DURATION:
        raise InvalidBookingDurationException(
            'Booking duration must be at least {0} minutes.'.format(MIN_BOOKING_DURATION_MINUTES)
        )
    if duration > MAX_DURATION:
        raise InvalidBookingDurationException(
            'Booking duration must be at most {0} hours.'.format(MAX_BOOKING_DURATION_HOURS)
        )


def validate_business_hours(start_time, end_time, tz_name):
    tz = resolve_timezone(tz_name)
    local_start = start_time.astimezone(tz)
    local_end = end_time.astimezone(tz)

    if local_start.date() != local_end.date():
        raise OutsideBusinessHoursException(
            'A booking must start and end on the same day (room local time).'
        )
    if local_start.weekday() not in BUSINESS_WEEKDAYS:
        raise OutsideBusinessHoursException(
            'Bookings are only allowed Monday to Friday (room local time).'
        )
    if local_start.time() < BUSINESS_START or local_end.time() > BUSINESS_END:
        raise OutsideBusinessHoursException(
            'Bookings are only allowed between 08:00 and 20:00 (room local time).'
        )


def business_hours_in_range(range_start, range_end, tz_name):
    if range_end <= range_start:
        return 0.0

    tz = resolve_timezone(tz_name)
    local_start = range_start.astimezone(tz)
    local_end = range_end.astimezone(tz)

    total = 0.0
    day = local_start.date()
    while day <= local_end.date():
        if day.weekday() in BUSINESS_WEEKDAYS:
            window_open = datetime.combine(day, BUSINESS_START, tzinfo=tz)
            window_close = datetime.combine(day, BUSINESS_END, tzinfo=tz)
            total += overlap_hours(window_open, window_close, local_start, local_end)
        day += timedelta(days=1)
    return total
