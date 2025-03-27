from rest_framework import status

from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_codes import ERROR_CODE_AUTH_USER_MUST_BE_AUTHENTICATED


class UserMustBeAuthenticated(CustomException):
    def __init__(self):
        super().__init__(message= "L'utilisateur doit être authentifié.'",
                         status_code=status.HTTP_403_FORBIDDEN,
                         code=ERROR_CODE_AUTH_USER_MUST_BE_AUTHENTICATED)