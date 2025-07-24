import json
from datetime import datetime

from background_task import background
from django.conf import settings
from django.utils import timezone
from mistralai import Mistral

from base.models.vocal import Vocal, VocalOrigine
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from sebania.utils.db_utils import get_ferme_for_user
from thomas_ai.tasks.extract import extract

mistral_api_key = settings.MISTRAL_API_KEY
mistral_client = Mistral(api_key=mistral_api_key)

@background(schedule=0, queue='analyze')
def analyze(vocal_id: int):
    # Récupération du vocal sans l'audio qui a déjà été traité
    vocal = Vocal.objects.defer('audio').get(id=vocal_id)
    if vocal.origine not in [VocalOrigine.TACHES, VocalOrigine.PARCELLES]:
        raise CustomException(ErrorCode.VOCAL_ORIGINE_INCORRECTE)

    # si la transcription est vide, on ne lance pas l'analyse et on marque le vocal comme étant analysé
    if (vocal.transcription is None) or (vocal.transcription == ''):
        vocal.finished_at = timezone.now()
        return

    start_time = datetime.now()
    # Récupération des parcelles de la ferme
    ferme = get_ferme_for_user(vocal.user.id)
    parcelles = ",".join([parcelle.nom for parcelle in ferme.parcelle_set.all()])

    # Analyse avec Mistral Agent
    chat_response = mistral_client.agents.complete(
        agent_id=_get_agent_id(vocal),
        messages=[
            {
                "role": "user",
                "content": _get_query(vocal, parcelles),
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
    if (output is not None) and (output != ''):
        vocal.output = json.loads(output)
    vocal.save()

    # Envoi dans la queue suivante pour l'extraction des tâches à partir du JSON généré
    extract(vocal_id=vocal_id)

def _get_agent_id(vocal: Vocal) -> str:
    return settings.MISTRAL_AGENTS[vocal.origine]

def _get_query(vocal: Vocal, parcelles) -> str:
    if vocal.origine == VocalOrigine.PARCELLES:
        return "{transcription}".format(transcription=vocal.transcription)
    elif vocal.origine == VocalOrigine.TACHES:
        return """
        Transcription: {transcription}
        Parcelles: {parcelles}
        """.format(transcription=vocal.transcription, parcelles=parcelles)
    else:
        return ""
