from rest_framework import status

from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_codes import ERROR_CODE_PARCELLE_TYPE_NOT_FOUND


class ParcelleTypeNotFoundException(CustomException):
    def __init__(self, type_id: int = None):
        super().__init__(message= "Le type parcelle id={} n'a pu être trouvé".format(type_id),
                         status_code=status.HTTP_404_NOT_FOUND,
                         code=ERROR_CODE_PARCELLE_TYPE_NOT_FOUND)