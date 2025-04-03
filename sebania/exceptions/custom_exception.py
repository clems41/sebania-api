import traceback

from rest_framework import status
from rest_framework.exceptions import APIException

from sebania.exceptions.error_code import ErrorCode


class CustomException(APIException):
    def __init__(self, message: str, code: ErrorCode, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, **kwargs):
        super().__init__()
        self.code = code
        self.message = message
        self.status_code  = status_code
