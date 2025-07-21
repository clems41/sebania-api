from base.models import User
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode


def validate_email(email: str):
    if email is None:
        raise CustomException(ErrorCode.USER_EMAIL_MUST_NOT_BE_EMPTY)
    if User.objects.filter(email=email).count() > 0:
        raise CustomException(ErrorCode.USER_EMAIL_ALREADY_EXISTS, email)