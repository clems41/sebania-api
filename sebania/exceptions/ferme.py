from rest_framework import status

from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode


class FermeNotFoundForUserException(CustomException):
    def __init__(self, user_id: int):
        super().__init__(message= "La ferme n'a pu être trouvée pour l'utilisateur id={}".format(user_id),
                         status_code=status.HTTP_404_NOT_FOUND,
                         code=ErrorCode.FERME_NOT_FOUND_FOR_USER)


class FermeNotFoundException(CustomException):
    def __init__(self, ferme_id: int):
        super().__init__(message= "La ferme id={} n'a pu être trouvée".format(ferme_id),
                         status_code=status.HTTP_404_NOT_FOUND,
                         code=ErrorCode.FERME_NOT_FOUND)