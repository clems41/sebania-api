from rest_framework import status

from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode


class ActiviteNotFoundException(CustomException):
    def __init__(self, activite_id: int):
        super().__init__(message= "L'activité id={} n'a pas pu être trouvé".format(activite_id),
                         status_code=status.HTTP_404_NOT_FOUND,
                         code=ErrorCode.ACTIVITE_NOT_FOUND)


class ActiviteQueryTooShortException(CustomException):
    def __init__(self, query: str):
        super().__init__(message= "Le paramètre 'query' doit au moins contenir 3 caractères, or il en contient {}".format(len(query.strip())),
                         status_code=status.HTTP_400_BAD_REQUEST,
                         code=ErrorCode.ACTIVITE_QUERY_TOO_SHORT)