import tempfile
from datetime import datetime
import requests

from background_task import background
from django.utils import timezone

from django.conf import settings

from base.models.vocal import Vocal
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from thomas_ai.tasks.analyze import analyze


@background(schedule=0, queue='transcription')
def transcribe(vocal_id: int):
    vocal = Vocal.objects.get(id=vocal_id)

    # Créer un fichier temporaire à partir du FieldFile pour la transcription
    start_time = datetime.now()
    with tempfile.NamedTemporaryFile(suffix=".m4a") as tmp_m4a_file:
        tmp_m4a_file.write(vocal.audio.read())
        tmp_m4a_file.flush()
        transcription = call_speech_to_text_api(tmp_m4a_file.name)

    # Mise à jour du vocal avec la transcription
    end_time = datetime.now()
    duration = end_time - start_time
    vocal.audio_to_transcription_duration = duration
    vocal.transcribed_at = timezone.now()
    vocal.transcription = transcription
    vocal.save()

    # Envoi dans la queue suivante pour l'analyse
    analyze(vocal_id=vocal_id)

def call_speech_to_text_api(filename: str):
    url = "https://api.lemonfox.ai/v1/audio/transcriptions"
    headers = {
        "Authorization": "Bearer " + settings.LEMONFOX_API_KEY,
    }
    data = {
        "language": "french",
        "response_format": "json"
    }

    files = {"file": open(filename, "rb")}
    response = requests.post(url, headers=headers, files=files, data=data)
    response_json = response.json()
    if response.status_code != 200:
        raise CustomException(ErrorCode.IA_LEMONFOX_API_ERROR, response_json)
    return response_json.get("text")