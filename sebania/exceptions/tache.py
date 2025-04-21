from sebania.exceptions.custom_exception import CustomException
from rest_framework import status

from sebania.exceptions.error_code import ErrorCode


class TacheCalendrierFiltreIncorrectException(CustomException):
    def __init__(self, semaine: int, mois: int):
        super().__init__(message= "Vous devez filtrer soit par mois, soit par semaine, pas les 2 ou aucun, or semaine={} et mois={}".format(semaine, mois),
                         status_code=status.HTTP_400_BAD_REQUEST,
                         code=ErrorCode.TACHE_CALENDRIER_FILTRE_INCORRECT)


class TacheCalendrierFiltreAnneeObligatoireException(CustomException):
    def __init__(self):
        super().__init__(message= "Le filtre année est obligatoire",
                         status_code=status.HTTP_400_BAD_REQUEST,
                         code=ErrorCode.TACHE_CALENDRIER_ANNEE_OBLIGATOIRE)


class TacheCalendrierFiltreUserIdObligatoireException(CustomException):
    def __init__(self):
        super().__init__(message= "Le filtre user_id est obligatoire",
                         status_code=status.HTTP_400_BAD_REQUEST,
                         code=ErrorCode.TACHE_CALENDRIER_USERID_OBLIGATOIRE)