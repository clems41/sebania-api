from rest_framework import status

from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode


class UserNotFoundException(CustomException):
    def __init__(self, user_id: int):
        super().__init__(message= "L'utilisateur id={} n'a pas pu être trouvé".format(user_id),
                         status_code=status.HTTP_404_NOT_FOUND,
                         code=ErrorCode.USER_NOT_FOUND)


class UserOldPasswordIncorrectException(CustomException):
    def __init__(self):
        super().__init__(message= "L'ancien mot de passe ne correspond pas".format(),
                         status_code=status.HTTP_403_FORBIDDEN,
                         code=ErrorCode.USER_OLD_PASSWORD_INCORRECT)