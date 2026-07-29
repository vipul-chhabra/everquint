

from rest_framework import status
from rest_framework.exceptions import APIException as DRFApiException
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

from core.constants import ERROR_INTERNAL, ERROR_VALIDATION


class BaseApiException(Exception):
    """
        Custom exception for our custom API.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    error = ERROR_VALIDATION
    default_detail = 'A request error occurred.'

    def __init__(self, message=None):
        self.message = message or self.default_detail
        super(BaseApiException, self).__init__(self.message)


class InvalidTimezoneException(BaseApiException):
    status_code = status.HTTP_400_BAD_REQUEST
    error = ERROR_VALIDATION
    default_detail = 'The provided timezone is not a valid IANA timezone.'


class InvalidQueryParameterException(BaseApiException):
    status_code = status.HTTP_400_BAD_REQUEST
    error = ERROR_VALIDATION
    default_detail = 'One or more query parameters are invalid.'


def first_error_message(detail):
    if isinstance(detail, dict):
        field, value = next(iter(detail.items()))
        message = first_error_message(value)
        return message if field == 'non_field_errors' else '{0}: {1}'.format(field, message)
    if isinstance(detail, (list, tuple)):
        return first_error_message(detail[0]) if detail else 'Invalid input.'
    return str(detail)


def custom_exception_handler(exc, context):
    """
    every exception is in the format: {error, message}.
    """
    # Our own domain exceptions already carry everything the envelope needs.
    if isinstance(exc, BaseApiException):
        return Response(
            {'error': exc.error, 'message': exc.message},
            status=exc.status_code,
        )
    if isinstance(exc, DRFApiException):
        is_validation = isinstance(exc, DRFValidationError)
        return Response(
            {
                'error': ERROR_VALIDATION if is_validation else exc.__class__.__name__,
                'message': first_error_message(exc.detail),
            },
            status=exc.status_code,
        )
    response = exception_handler(exc, context)
    if response is not None:
        return response
    return Response(
        {
            'error': ERROR_INTERNAL,
            'message': 'An unexpected error occurred. Please contact support.',
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
