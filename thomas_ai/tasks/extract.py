import logging

from background_task import background
from django.utils import timezone

from base.models.vocal import Vocal
from thomas_ai.serialzers.tache import TacheOutputSerializer


# Get an instance of a logger
logger = logging.getLogger(__name__)

@background(schedule=0, queue='extract')
def extract(vocal_id: int):
    # Récupération du vocal sans l'audio et la transcription qui ont déjà été traités
    vocal = Vocal.objects.defer('audio', 'transcription').get(id=vocal_id)
    errors = []
    for output_tache in vocal.output:
        serializer = TacheOutputSerializer(data=output_tache, context={'vocal_id': vocal_id})
        if serializer.is_valid():
            serializer.save()
        else:
            errors.append(serializer.errors)
            logger.error("Une erreur est survenue lors de l'extraction de la tâche pour le vocal id={} : {}".format(vocal.id, serializer.errors))

    # Mise à jour du vocal avec l'extract
    vocal.finished_at = timezone.now()
    if len(errors) > 0:
        vocal.errors = errors
    vocal.save()