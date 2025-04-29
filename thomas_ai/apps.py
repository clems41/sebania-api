import logging

from django.apps import AppConfig
import whisper

from django.conf import settings

# Get an instance of a logger
logger = logging.getLogger(__name__)

class ThomasAiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'thomas_ai'

    def ready(self):
        # download whisper model to avoid doing it during first task processing
        logger.info("Téléchargement du modèle '{}' de Whisper dans le dossier {}".format(settings.WHISPER_MODEL, settings.WHISPER_MODEL_DIRECTORY))
        whisper.load_model(settings.WHISPER_MODEL, download_root=settings.WHISPER_MODEL_DIRECTORY)
