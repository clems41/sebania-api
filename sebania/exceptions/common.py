from rest_framework import status

from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_codes import ERROR_CODE_GLOBAL_UNKNOWN_ERROR


class UnknownErrorException(CustomException):
    def __init__(self, exception: Exception):
        super().__init__(message=repr(exception),
                         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                         code=ERROR_CODE_GLOBAL_UNKNOWN_ERROR)