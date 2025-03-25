import random
import string

from django.conf import settings


def generate_password():
    alphabet = string.ascii_letters + string.digits
    return ''.join(random.choice(alphabet) for _ in range(settings.DEFAULT_PASSWORD_LENGTH))

def random_string(length: int = 10, lowercase_only: bool = True, digit: bool = False) -> str:
    if lowercase_only:
        alphabet = string.ascii_lowercase
    else:
        alphabet = string.ascii_letters
    if digit:
        alphabet += string.digits
    return ''.join(random.choice(alphabet) for _ in range(length))

def random_email() -> str:
    return random_string(15) + "@" + random_string(8) + ".com"