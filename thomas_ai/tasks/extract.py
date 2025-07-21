import logging

from background_task import background
from django.utils import timezone

from base.models.vocal import Vocal, VocalOrigine
from base.serializers.parcelle import ParcelleOutputSerializer
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from sebania.utils.db_utils import get_ferme_for_user
from thomas_ai.serialzers.tache import TacheOutputSerializer


# Get an instance of a logger
logger = logging.getLogger(__name__)

@background(schedule=0, queue='extract')
def extract(vocal_id: int):
    # Récupération du vocal sans l'audio et la transcription qui ont déjà été traités
    vocal = Vocal.objects.defer('audio', 'transcription').get(id=vocal_id)

    if vocal.origine == VocalOrigine.TACHES:
        errors = _extract_taches(vocal)
    elif vocal.origine == VocalOrigine.PARCELLES:
        errors = _extract_parcelles(vocal)
    else:
        raise CustomException(ErrorCode.VOCAL_ORIGINE_INCORRECTE)

    # Mise à jour du vocal avec l'extract
    vocal.finished_at = timezone.now()
    if len(errors) > 0:
        vocal.errors = errors
    vocal.save()

def _extract_taches(vocal: Vocal):
    errors = []
    for output_tache in vocal.output:
        serializer = TacheOutputSerializer(data=output_tache, context={'vocal_id': vocal.id})
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
        except Exception as e:
            errors.append(repr(e))
            logger.error("Une erreur est survenue lors de l'extraction de la tâche pour le vocal id={} : {}".format(vocal.id, repr(e)))
    return errors


def _extract_parcelles(vocal: Vocal):
    errors = []
    ferme = get_ferme_for_user(vocal.user.id)
    for output_parcelle in vocal.output:
        serializer = ParcelleOutputSerializer(data=output_parcelle, context={'ferme': ferme})
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
        except Exception as e:
            errors.append(repr(e))
            logger.error("Une erreur est survenue lors de l'extraction de la parcelle pour le vocal id={} : {}".format(vocal.id, repr(e)))
    return errors