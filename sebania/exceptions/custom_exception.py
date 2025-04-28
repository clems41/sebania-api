import traceback

from rest_framework import status
from rest_framework.exceptions import APIException

from sebania.exceptions.error_code import ErrorCode


class CustomException(APIException):
    def __init__(self, error_code: ErrorCode, *args, **kwargs):
        super().__init__()
        self.code = error_code.name
        self.message = error_code.value[0].format(*args, **kwargs)
        self.status_code  = error_code.value[1]
