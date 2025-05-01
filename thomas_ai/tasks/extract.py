from background_task import background
from django.utils import timezone

from base.models.vocal import Vocal
from thomas_ai.serialzers.tache import TacheOutputSerializer


@background(schedule=0, queue='extract')
def extract(vocal_id: int):
    # Récupération du vocal sans l'audio et la transcription qui ont déjà été traités
    vocal = Vocal.objects.defer('audio', 'transcription', 'transcription_improved').get(id=vocal_id)
    for output_tache in vocal.output:
        output_tache["vocal_id"] = vocal_id
        serializer = TacheOutputSerializer(data=output_tache, context={'vocal_id': vocal_id})
        if serializer.is_valid():
            serializer.save()

    # Mise à jour du vocal avec l'extract
    vocal.finished_at = timezone.now()
    vocal.save()