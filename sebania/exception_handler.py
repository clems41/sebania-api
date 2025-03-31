import traceback

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import exception_handler

from base.models.error import Error
from sebania.exceptions.common import UnknownErrorException
from sebania.exceptions.custom_exception import CustomException


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

    # Handle custom exceptions
    if len(exc.__class__.__bases__) > 0 and exc.__class__.__bases__[0].__name__ == 'CustomException':
        return ErrorResponse(exc)

    # If no response, it means that we are facing error 500 : we should create response based on the exception
    if response is None:
        _save_error(exc, context)
        return ErrorResponse(UnknownErrorException(exc))


    return response

def _save_error(exc, context):
    request = context.get('request')
    user = None
    if request.user.is_authenticated:
        user = request.user
    Error.objects.create(message=repr(exc), traceback=traceback.format_exc(), url=request.get_full_path(),
                         query_params=request.query_params.dict(), body= request.data, user=user)