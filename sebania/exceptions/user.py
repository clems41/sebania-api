from rest_framework import status

from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_codes import ERROR_CODE_USER_NOT_FOUND


class UserNotFoundException(CustomException):
    def __init__(self, user_id: int = None):
        super().__init__(message= "L'utilisateur id={} n'a pas pu être trouvé".format(user_id),
                         status_code=status.HTTP_404_NOT_FOUND,
                         code=ERROR_CODE_USER_NOT_FOUND)