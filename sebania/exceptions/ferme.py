from rest_framework import status

from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_codes import ERROR_CODE_FERME_NOT_FOUND_FOR_USER


class FermeNotFoundForUserException(CustomException):
    def __init__(self, user_id: int = None):
        super().__init__(message= "La ferme n'a pu être trouvée pour l'utilisateur id={}".format(user_id),
                         status_code=status.HTTP_404_NOT_FOUND,
                         code=ERROR_CODE_FERME_NOT_FOUND_FOR_USER)