import tempfile
from datetime import datetime
from faster_whisper import WhisperModel

from background_task import background
from django.utils import timezone

from django.conf import settings

from base.models.vocal import Vocal
from thomas_ai.tasks.analyze import analyze


@background(schedule=0, queue='transcription')
def transcribe(vocal_id: int):
    vocal = Vocal.objects.get(id=vocal_id)
    # Run on GPU with FP16
    # model = WhisperModel(model_size, device="cuda", compute_type="float16")
    # or run on GPU with INT8
    # model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
    # or run on CPU with INT8
    model = WhisperModel(settings.WHISPER_MODEL, device="cpu", compute_type="int8", download_root=settings.WHISPER_MODEL_DIRECTORY)

    # Créer un fichier temporaire à partir du FieldFile pour la transcription
    start_time = datetime.now()
    with tempfile.NamedTemporaryFile(suffix=".mp3") as tmp:
        tmp.write(vocal.audio.read())
        tmp.flush()
        segments, _ = model.transcribe(tmp.name, language="fr", log_progress=settings.DEBUG)
        transcription = "".join([segment.text for segment in list(segments)])

    # Mise à jour du vocal avec la transcription
    end_time = datetime.now()
    duration = end_time - start_time
    vocal.audio_to_transcription_duration = duration
    vocal.transcribed_at = timezone.now()
    vocal.transcription = transcription
    vocal.save()

    # Envoi dans la queue suivante pour l'analyse
    analyze(vocal_id=vocal_id)