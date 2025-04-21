import re
import traceback

from django.conf import settings
from jsonschema.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

from base.models.error import Error
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode, get_error_code_from_str


class ErrorResponse(Response):
    def __init__(self, custom_exception: CustomException, **kwargs):
        data = {
            "message": custom_exception.message,
            "code": custom_exception.code,
        }
        if settings.DEBUG:
            data["traceback"] = traceback.format_exc()
        super().__init__(data=data, status=custom_exception.status_code)


def extract_error_code_from_validation_error(exception: ValidationError):
    message = repr(exception)
    match = re.search(r"string='([^']+)'", message)
    if match:
        code = match.group(1)
        return get_error_code_from_str(code)
    else:
        return None

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Handle custom exceptions
    if exc.__class__.__name__ == 'CustomException':
        return ErrorResponse(exc)

    # Handle validation error
    if exc.__class__.__name__ == 'ValidationError':
        error_code = extract_error_code_from_validation_error(exc)
        if error_code is not None:
            custom_exception = CustomException(error_code)
            return ErrorResponse(custom_exception)

    # If no response, it means that we are facing error 500 : we should create response based on the exception
    if response is None:
        _save_error(exc, context)
        return ErrorResponse(CustomException(ErrorCode.GLOBAL_UNKNOWN_ERROR, repr(exc)))


    return response

def _save_error(exc, context):
    request = context.get('request')
    user = None
    if request.user.is_authenticated:
        user = request.user
    Error.objects.create(message=repr(exc), traceback=traceback.format_exc(), url=request.get_full_path(),
                         query_params=request.query_params.dict(), body= request.data, user=user)