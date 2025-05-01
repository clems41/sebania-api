import json
from datetime import datetime

from background_task import background
from django.utils import timezone

from base.models import Culture, Activite, Unite
from base.models.vocal import Vocal
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from thomas_ai.crewai.crew import AnalyzerCrew
from thomas_ai.tasks.extract import extract


@background(schedule=0, queue='analyze')
def analyze(vocal_id: int):
    # Récupération du vocal sans l'audio qui a déjà été traité
    vocal = Vocal.objects.defer('audio').get(id=vocal_id)

    # Analyse avec CrewAI
    start_time = datetime.now()
    inputs = _get_inputs()
    inputs['transcription'] = vocal.transcription
    crew = AnalyzerCrew()
    outputs = crew.crew().kickoff(inputs=inputs)

    # Check output
    if len(outputs.tasks_output) != crew.get_nb_agents():
        raise CustomException(ErrorCode.IA_CREWAI_OUTPUT_LEN_INCORRECTE, actual=len(outputs.tasks_output), expected=crew.get_nb_agents())
    output = outputs.tasks_output[crew.get_nb_agents() - 1].raw
    transcription_improved = outputs.tasks_output[0].raw

    # Mise à jour du vocal avec l'analyse
    end_time = datetime.now()
    duration = end_time - start_time
    vocal.transcription_to_output_duration = duration
    vocal.analyzed_at = timezone.now()
    vocal.output = _cleanup_output(output)
    vocal.transcription_improved = transcription_improved
    vocal.save()

    # Envoi dans la queue suivante pour l'extraction des tâches à partir du JSON généré
    extract(vocal_id=vocal_id)

def _get_inputs():
    cultures = Culture.objects.all()
    activites = Activite.objects.all()
    unites = Unite.objects.all()
    culture_noms = [c.nom for c in cultures]
    activite_noms = [a.nom for a in activites]
    unite_noms = [u.nom for u in unites]
    return {
        'cultures': ','.join(culture_noms),
        'activites': ','.join(activite_noms),
        'unites': ','.join(unite_noms)
    }

def _cleanup_output(output):
    output = output.replace('```json\n', '').replace('\n```', '')
    return json.loads(output)