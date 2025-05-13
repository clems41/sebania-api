import datetime
from xmlrpc.client import Fault

from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ModelViewSet, GenericViewSet

from base.models.vocal import Vocal
from base.serializers.vocal import VocalSerializer, SendVocalSerializer
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from sebania.utils.db_utils import get_one_or_raise_exception
from thomas_ai.tasks.transcription import transcribe


@extend_schema_view(
    create=extend_schema(exclude=True),   # cache POST de Swagger
    update=extend_schema(exclude=True),   # cache PUT de Swagger
)
class VocalViewSet(ModelViewSet):
    serializer_class = VocalSerializer
    parser_classes = [FileUploadParser]
    queryset = Vocal.objects.defer('audio').all()
    http_method_names = ['get', 'post']  # pas de 'put' ni 'delete'

    def create(self, request, *args, **kwargs):
        raise CustomException(ErrorCode.GLOBAL_METHOD_NOT_ALLOWED)

    def list(self, request, *args, **kwargs):
        raise CustomException(ErrorCode.GLOBAL_METHOD_NOT_ALLOWED)

    @extend_schema(description="Envoi d'un message vocal à Thomas", responses=VocalSerializer)
    @action(detail=False, methods=['post'], url_path=r'date/(?P<date>\w+)', serializer_class=SendVocalSerializer)
    def send_vocal(self, request, date: str = None):
        try:
            validated_date = datetime.datetime.strptime(date, "%d%m%Y").date()
        except:
            raise CustomException(ErrorCode.VOCAL_DATE_INCORRECTE, date)
        form = SendVocalSerializer(request.POST, request.FILES)
        if not form.is_valid():
            raise CustomException(ErrorCode.VOCAL_FILE_UPLOAD, form.errors)
        file = form.validated_data['file']
        vocal = Vocal.objects.create(audio=file, user=request.user, date=validated_date)
        transcribe(vocal_id=vocal.id)
        return Response(VocalSerializer(vocal).data, status=status.HTTP_201_CREATED)

    @extend_schema(description="Récupération du statut d'un vocal", responses=VocalSerializer)
    def retrieve(self, request, pk =None):
        vocal = get_one_or_raise_exception(Vocal, CustomException(ErrorCode.VOCAL_NOT_FOUND, pk), defer_fields=["audio"], id=pk)
        if request.user.id != vocal.user.id:
            raise CustomException(ErrorCode.VOCAL_NOT_FOUND, pk)
        return Response(VocalSerializer(vocal).data, status=status.HTTP_200_OK)


    @extend_schema(description="Récupération des vocaux en cours de traitement pour une date donnée",
                   parameters=[
                       OpenApiParameter("date", str, required=True, description="Date des vocaux au format dd/MM/YYYY"),
                   ])
    def list(self, request):
        query_params = request.query_params.dict()
        if 'date' not in query_params:
            raise CustomException(ErrorCode.VOCAL_DATE_MANQUANTE)
        date = query_params.get('date')
        try:
            validated_date = datetime.datetime.strptime(date, "%d/%m/%Y")
        except:
            raise CustomException(ErrorCode.VOCAL_DATE_INCORRECTE, date)
        vocaux = Vocal.objects.defer('audio').filter(date=validated_date, user=request.user, finished_at__isnull=True)
        return Response(VocalSerializer(vocaux, many=True).data, status=status.HTTP_200_OK)