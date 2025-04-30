import logging

from django.apps import AppConfig

# Get an instance of a logger
logger = logging.getLogger(__name__)

class ThomasAiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'thomas_ai'
