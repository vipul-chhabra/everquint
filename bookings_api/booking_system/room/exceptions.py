from rest_framework import status

from core.constants import ERROR_NOT_FOUND, ERROR_VALIDATION
from core.exceptions import BaseApiException


class RoomNameAlreadyExistsException(BaseApiException):
    status_code = status.HTTP_400_BAD_REQUEST
    error = ERROR_VALIDATION
    default_detail = 'A room with this name already exists.'


class RoomNotFoundException(BaseApiException):
    status_code = status.HTTP_404_NOT_FOUND
    error = ERROR_NOT_FOUND
    default_detail = 'The requested room does not exist.'
