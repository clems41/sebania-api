import datetime

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from base.models.vocal import Vocal
from base.serializers.thomas import VocalSerializer, SendVocalSerializer
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode


class ThomasViewSet(ViewSet):
    serializer_class = VocalSerializer
    parser_classes = [FileUploadParser]
    queryset = None

    @extend_schema(description="Envoi d'un message vocal à Thomas", responses=VocalSerializer)
    @action(detail=False, methods=['post'], url_path='vocal/(?P<date>\w+)', serializer_class=SendVocalSerializer,
            url_name="vocal")
    def send_vocal(self, request, date: str = None):
        try:
            validated_date = datetime.datetime.strptime(date, "%d%m%Y")
        except:
            raise CustomException(ErrorCode.VOCAL_DATE_INCORRECTE, date)
        form = SendVocalSerializer(request.POST, request.FILES)
        if not form.is_valid():
            raise CustomException(ErrorCode.VOCAL_FILE_UPLOAD, form.errors)
        file = form.validated_data['file']
        vocal = Vocal.objects.create(audio=file, user=request.user, date=validated_date)
        return Response(VocalSerializer(vocal).data, status=status.HTTP_201_CREATED)