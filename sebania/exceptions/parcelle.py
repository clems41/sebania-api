from rest_framework import status

from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode


class ParcelleTypeNotFoundException(CustomException):
    def __init__(self, type_id: int):
        super().__init__(message= "Le type parcelle id={} n'a pu être trouvé".format(type_id),
                         status_code=status.HTTP_404_NOT_FOUND,
                         code=ErrorCode.PARCELLE_TYPE_NOT_FOUND)

class ParcelleNotFoundException(CustomException):
    def __init__(self, parcelle_id: int, ferme_id: int):
        super().__init__(message= "La parcelle id={} n'a pu être trouvée pour la ferme id={}".format(parcelle_id, ferme_id),
                         status_code=status.HTTP_404_NOT_FOUND,
                         code=ErrorCode.PARCELLE_NOT_FOUND)