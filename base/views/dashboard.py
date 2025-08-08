from base.serializers.dashboard.activite import ActivitesDashboardSerializer
from rest_framework.response import Response
from rest_framework.views import APIView

from base.models import Ferme
from base.serializers.dashboard.culture import CulturesDashboardSerializer
from base.serializers.dashboard.parcelle import ParcellesDashboardSerializer
from base.serializers.dashboard.temps_travail import DureeParJourDashboardSerializer, \
    TempsTravailCardsDashboardSerializer
from base.serializers.dashboard.vue_ensemble import VueEnsembleCardsSerializer
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from sebania.utils.db_utils import get_one_or_raise_exception


class DashboardActivitesView(APIView):
    def get(self, request):
        ferme = get_one_or_raise_exception(Ferme, CustomException(ErrorCode.FERME_NOT_FOUND_FOR_USER, request.user.id),
                                           responsable=request.user)
        data = ActivitesDashboardSerializer.get_data(ferme, request.query_params)
        return Response({'data': data})

class DashboardCulturesView(APIView):
    def get(self, request):
        ferme = get_one_or_raise_exception(Ferme, CustomException(ErrorCode.FERME_NOT_FOUND_FOR_USER, request.user.id),
                                           responsable=request.user)
        data = CulturesDashboardSerializer.get_data(ferme, request.query_params)
        return Response({'data': data})

class DashboardParcellesView(APIView):
    def get(self, request):
        ferme = get_one_or_raise_exception(Ferme, CustomException(ErrorCode.FERME_NOT_FOUND_FOR_USER, request.user.id),
                                           responsable=request.user)
        data = ParcellesDashboardSerializer.get_data(ferme, request.query_params)
        return Response({'data': data})

class DashboardTempsTravailView(APIView):
    def get(self, request):
        ferme = get_one_or_raise_exception(Ferme, CustomException(ErrorCode.FERME_NOT_FOUND_FOR_USER, request.user.id),
                                           responsable=request.user)
        data = DureeParJourDashboardSerializer.get_data(ferme, request.query_params)
        return Response({'data': data})

class DashboardTempsTravailCardsView(APIView):
    def get(self, request):
        ferme = get_one_or_raise_exception(Ferme, CustomException(ErrorCode.FERME_NOT_FOUND_FOR_USER, request.user.id),
                                           responsable=request.user)
        data = TempsTravailCardsDashboardSerializer.get_data(ferme, request.query_params)
        return Response(data)

class DashboardVueEnsembleCardsView(APIView):
    def get(self, request):
        ferme = get_one_or_raise_exception(Ferme, CustomException(ErrorCode.FERME_NOT_FOUND_FOR_USER, request.user.id),
                                           responsable=request.user)
        serializer = VueEnsembleCardsSerializer(ferme)
        return Response(serializer.data)
