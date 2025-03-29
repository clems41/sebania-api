from rest_framework import status

from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_codes import ERROR_CODE_GLOBAL_UNKNOWN_ERROR, ERROR_CODE_GLOBAL_WRONG_ARG


class UnknownErrorException(CustomException):
    def __init__(self, exception: Exception):
        super().__init__(message=repr(exception),
                         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                         code=ERROR_CODE_GLOBAL_UNKNOWN_ERROR)

class WrongArgForMethodException(CustomException):
    def __init__(self, must_be: str, actual: str, method: str):
        super().__init__(message="La méthode {} ne peut pas être appelée avec un argument de type {}, uniquement avec les types suivantes : {}".format(method, actual, must_be),
                         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                         code=ERROR_CODE_GLOBAL_WRONG_ARG)