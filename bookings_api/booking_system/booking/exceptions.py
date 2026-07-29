
from rest_framework import status

from core.constants import ERROR_CONFLICT, ERROR_NOT_FOUND, ERROR_VALIDATION
from core.exceptions import BaseApiException


class InvalidTimeRangeException(BaseApiException):
    status_code = status.HTTP_400_BAD_REQUEST
    error = ERROR_VALIDATION
    default_detail = 'startTime must be before endTime.'


class InvalidBookingDurationException(BaseApiException):
    status_code = status.HTTP_400_BAD_REQUEST
    error = ERROR_VALIDATION
    default_detail = 'Booking duration must be between 15 minutes and 4 hours.'


class OutsideBusinessHoursException(BaseApiException):
    status_code = status.HTTP_400_BAD_REQUEST
    error = ERROR_VALIDATION
    default_detail = 'Bookings are only allowed on Monday to Friday, 08:00-20:00.'


class BookingOverlapException(BaseApiException):
    status_code = status.HTTP_409_CONFLICT
    error = ERROR_CONFLICT
    default_detail = 'The room is already booked for the time range.'


class IdempotencyInProgressException(BaseApiException):
    status_code = status.HTTP_409_CONFLICT
    error = ERROR_CONFLICT
    default_detail = 'A booking request with this Idempotency-Key is already in progress.'


class BookingNotFoundException(BaseApiException):
    status_code = status.HTTP_404_NOT_FOUND
    error = ERROR_NOT_FOUND
    default_detail = 'The requested booking does not exist.'


class CancellationWindowClosedException(BaseApiException):
    status_code = status.HTTP_400_BAD_REQUEST
    error = ERROR_VALIDATION
    default_detail = 'A booking can only be cancelled up to 1 hour before its start time.'
