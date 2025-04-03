from rest_framework import status

from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode


class ActiviteNotFoundException(CustomException):
    def __init__(self, activite_id: int):
        super().__init__(message= "L'activité id={} n'a pas pu être trouvé".format(activite_id),
                         status_code=status.HTTP_404_NOT_FOUND,
                         code=ErrorCode.ACTIVITE_NOT_FOUND)