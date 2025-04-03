from rest_framework import status

from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode


class CultureNotFoundException(CustomException):
    def __init__(self, culture_id: int):
        super().__init__(message= "La culture id={} n'a pas pu être trouvée".format(culture_id),
                         status_code=status.HTTP_404_NOT_FOUND,
                         code=ErrorCode.CULTURE_NOT_FOUND)