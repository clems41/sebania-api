import datetime
from xmlrpc.client import Fault

from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from base.models.vocal import Vocal
from base.serializers.thomas import VocalSerializer, SendVocalSerializer
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from sebania.utils.db_utils import get_one_or_raise_exception, get_ferme_for_user


class ThomasViewSet(ViewSet):
    serializer_class = VocalSerializer
    parser_classes = [FileUploadParser]
    queryset = None

    @extend_schema(description="Envoi d'un message vocal à Thomas", responses=VocalSerializer)
    @action(detail=False, methods=['post'], url_path='vocal/date/(?P<date>\w+)', serializer_class=SendVocalSerializer,
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

    @extend_schema(description="Récupération du statut d'un vocal")
    @action(detail=False, methods=['get'], url_path='vocal/(?P<id>\w+)', serializer_class=VocalSerializer,
            url_name="get-vocal")
    def get_vocal(self, request, id: int =None):
        vocal = get_one_or_raise_exception(Vocal, CustomException(ErrorCode.VOCAL_NOT_FOUND, id), id=id)
        if request.user.id != vocal.user.id:
            CustomException(ErrorCode.VOCAL_NOT_FOUND, id)
        return Response(VocalSerializer(vocal).data, status=status.HTTP_201_CREATED)

    @extend_schema(description="Récupération des vocaux en cours de traitement pour une date donnée",
                   parameters=[
                       OpenApiParameter("date", str, required=True, description="Date des vocaux au format ddMMYYYY"),
                   ],)
    @action(detail=False, methods=['get'], url_path='vocal/processing', serializer_class=VocalSerializer,
            url_name="vocal-processing")
    def get_vocal(self, request):
        query_params = request.query_params.dict()
        if 'date' not in query_params:
            raise CustomException(ErrorCode.VOCAL_DATE_MANQUANTE)
        date = query_params.get('date')
        try:
            validated_date = datetime.datetime.strptime(date, "%d%m%Y")
        except:
            raise CustomException(ErrorCode.VOCAL_DATE_INCORRECTE, date)
        vocaux = Vocal.objects.filter(date=validated_date, user=request.user)
        return Response(VocalSerializer(vocaux, many=True).data, status=status.HTTP_200_OK)