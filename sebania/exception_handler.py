import logging
import re
import traceback

from django.conf import settings
from jsonschema.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework import status

from base.models.error import Error
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode, get_error_code_from_str
from sebania.utils.email_utils import send_error500

# Get an instance of a logger
logger = logging.getLogger(__name__)

class ErrorResponse(Response):
    def __init__(self, custom_exception: CustomException, **kwargs):
        data = {
            "message": custom_exception.message,
            "code": custom_exception.code,
        }
        if settings.DEBUG:
            data["traceback"] = traceback.format_exc()
        super().__init__(data=data, status=custom_exception.status_code)


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Handle exceptions
    exc_class_name = exc.__class__.__name__

    # Handle custom exceptions
    if exc_class_name == 'CustomException':
        return ErrorResponse(exc)
    # Handle validation error using custom exception
    elif exc_class_name == 'ValidationError':
        return ErrorResponse(_get_custom_exception_from_validation_error(exc))

    # If no response, it means that we are facing error 500 : we should create response based on the exception
    if response is None or response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        _save_error(exc, context)
        return ErrorResponse(_get_unknown_error(exc))


    return response

def _save_error(exc, context):
    request = context.get('request')
    user = None
    if request.user.is_authenticated:
        user = request.user
    if "file" in request.data:
        request.data.pop("file") # file cannot be store in database
    try:
        send_error500(request.get_full_path(), user.id if user else 0, repr(exc))
        Error.objects.create(message=repr(exc), traceback=traceback.format_exc(), url=request.get_full_path(),
                         query_params=request.query_params.dict(), body=request.data, user=user)
    except Exception as e:
        logger.error('Error while saving error : ', e)


def _extract_error_code_from_validation_error(exception: ValidationError):
    message = repr(exception)
    match = re.search(r"string='([^']+)'", message)
    if match:
        code = match.group(1)
        return get_error_code_from_str(code)
    else:
        return None


def _get_custom_exception_from_validation_error(exception: ValidationError):
    error_code = _extract_error_code_from_validation_error(exception)
    if error_code is not None:
        return CustomException(error_code)
    return CustomException(ErrorCode.GLOBAL_VALIDATION_ERROR, repr(exception))


def _get_unknown_error(exception: Exception):
    return CustomException(ErrorCode.GLOBAL_UNKNOWN_ERROR, repr(exception))