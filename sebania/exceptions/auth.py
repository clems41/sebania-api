from rest_framework import status

from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode


class UserMustBeAuthenticatedException(CustomException):
    def __init__(self):
        super().__init__(message= "L'utilisateur doit être authentifié.'",
                         status_code=status.HTTP_403_FORBIDDEN,
                         code=ErrorCode.AUTH_USER_MUST_BE_AUTHENTICATED)

class EmployeCannotPostForResponsableException(CustomException):
    def __init__(self):
        super().__init__(message= "Les employés ne peuvent pas saisir pour les responsables ou les autres employés",
                         status_code=status.HTTP_403_FORBIDDEN,
                         code=ErrorCode.AUTH_EMPLOYE_CANNOT_POST_FOR_RESPONSABLE)