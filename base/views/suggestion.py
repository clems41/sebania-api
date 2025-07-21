from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from base.models import Activite, Culture
from base.models.tache import CultureTache, Tache
from base.serializers.parcelle import ParcelleSerializer
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from sebania.utils.db_utils import get_ferme_from_request, get_one_or_raise_exception


class SuggestionViewSet(GenericViewSet):
    serializer_class = None
    queryset = None

    @extend_schema(description="Liste des parcelles à suggérer lors de la saisie d'une tâche pour une activité et une culture donnée",
                   parameters=[
                       OpenApiParameter(name="culture_id", required=True, description="ID de la culture"),
                       OpenApiParameter(name="activite_id", required=True, description="ID de l'activite")
                   ],
                   responses=ParcelleSerializer(many=True))
    @action(detail=False, methods=['get'], url_path='parcelles', serializer_class=ParcelleSerializer)
    def get_parcelles(self, request):
        if 'culture_id' not in request.query_params:
            raise CustomException(ErrorCode.SUGGESTIONS_CULTURE_MISSING)
        if 'activite_id' not in request.query_params:
            raise CustomException(ErrorCode.SUGGESTIONS_ACTIVITE_MISSING)
        ferme = get_ferme_from_request(request)
        activite_id = request.query_params["activite_id"]
        culture_id = request.query_params["culture_id"]
        activite = get_one_or_raise_exception(Activite, CustomException(ErrorCode.ACTIVITE_NOT_FOUND, activite_id), id=activite_id)
        culture = get_one_or_raise_exception(Culture, CustomException(ErrorCode.CULTURE_NOT_FOUND, culture_id), id=culture_id)
        parcelles = []
        if activite.id not in [7 , 8]: # cas autres que plantation ou semis direct
            match activite.niveau_complexite:
                case 3 | 4 | 7 | 8:
                    previous_tache = Tache.objects.filter(cultures__culture_id=culture.id, ferme=ferme).order_by("-date").first()
                    if previous_tache is not None:
                        for culture_tache in previous_tache.cultures.all():
                            if culture_tache.culture_id == culture.id:
                                parcelles = culture_tache.parcelles
        return Response(ParcelleSerializer(parcelles, many=True).data)