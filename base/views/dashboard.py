from datetime import datetime

from django.db.models import Q
from django.db.models.aggregates import Sum, Count
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from base.models import Ferme, Tache
from base.serializers.dashboard.vue_ensemble import VueEnsembleCardsSerializer
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from sebania.permissions import HasResponsablePermission
from sebania.utils.db_utils import get_one_or_raise_exception


class DashboardVueEnsembleViewSet(ViewSet):
    serializer_class = None
    permission_classes = [IsAuthenticated, HasResponsablePermission]

    @extend_schema(responses=VueEnsembleCardsSerializer,
                   description="Récupération des données pour les cards de la page vue d'ensemble")
    @action(detail=False, methods=['get'], url_path='cards', serializer_class=VueEnsembleCardsSerializer, url_name="cards")
    def cards(self, request):
        ferme = get_one_or_raise_exception(Ferme, CustomException(ErrorCode.FERME_NOT_FOUND_FOR_USER, request.user.id),
                                           responsable=request.user)
        serializer = VueEnsembleCardsSerializer(ferme)
        return Response(serializer.data)
