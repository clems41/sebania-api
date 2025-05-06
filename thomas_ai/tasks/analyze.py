import json
from datetime import datetime

from background_task import background
from django.conf import settings
from django.utils import timezone
from mistralai import Mistral

from base.models.vocal import Vocal
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from thomas_ai.tasks.extract import extract

mistral_api_key = settings.MISTRAL_API_KEY
mistral_client = Mistral(api_key=mistral_api_key)

@background(schedule=0, queue='analyze')
def analyze(vocal_id: int):
    # Récupération du vocal sans l'audio qui a déjà été traité
    vocal = Vocal.objects.defer('audio').get(id=vocal_id)

    # Analyse avec Mistral Agent
    start_time = datetime.now()
    chat_response = mistral_client.agents.complete(
        agent_id="ag:76bf0d16:20250506:untitled-agent:9faabefa",
        messages=[
            {
                "role": "user",
                "content": vocal.transcription,
            },
        ],
    )

    # Check output
    if len(chat_response.choices) == 0:
        raise CustomException(ErrorCode.IA_OUTPUT_LEN_INCORRECTE, actual=0, expected=1)
    output = chat_response.choices[0].message.content

    # Mise à jour du vocal avec l'analyse
    end_time = datetime.now()
    duration = end_time - start_time
    vocal.transcription_to_output_duration = duration
    vocal.analyzed_at = timezone.now()
    vocal.output = json.loads(output)
    vocal.save()

    # Envoi dans la queue suivante pour l'extraction des tâches à partir du JSON généré
    extract(vocal_id=vocal_id)