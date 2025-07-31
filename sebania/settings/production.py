# SECURITY WARNING: don't run with debug turned on in production!
from .base import *

CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ORIGIN_WHITELIST").split(",")

DEBUG = True

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=100),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
    'SLIDING_TOKEN_LIFETIME': timedelta(days=30),
    'SLIDING_TOKEN_REFRESH_LIFETIME_LATE_USER': timedelta(days=1),
    'SLIDING_TOKEN_LIFETIME_LATE_USER': timedelta(days=30),
    'UPDATE_LAST_LOGIN': True,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'faster_whisper': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


SWAGGER_ENABLE = True
ADMIN_ENABLE = True