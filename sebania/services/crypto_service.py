import secrets
import string

from django.conf import settings


def generate_password():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(settings.DEFAULT_PASSWORD_LENGTH))