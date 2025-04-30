import tempfile
from datetime import datetime
import whisper

from background_task import background
from django.utils import timezone

from django.conf import settings

from base.models.vocal import Vocal
from thomas_ai.tasks.analyze import analyze


@background(schedule=0, queue='transcription')
def transcribe(vocal_id: int):
    vocal = Vocal.objects.get(id=vocal_id)
    model = whisper.load_model(settings.WHISPER_MODEL, download_root=settings.WHISPER_MODEL_DIRECTORY)

    # Créer un fichier temporaire à partir du FieldFile pour la transcription
    start_time = datetime.now()
    with tempfile.NamedTemporaryFile(suffix=".mp3") as tmp:
        tmp.write(vocal.audio.read())
        tmp.flush()
        result = model.transcribe(tmp.name, language="fr", verbose=True, fp16=False)

    end_time = datetime.now()
    duration = end_time - start_time
    vocal.audio_to_transcription_duration = duration
    vocal.transcribed_at = timezone.now()
    vocal.transcription = result["text"]
    vocal.save()
    analyze(vocal_id=vocal_id)