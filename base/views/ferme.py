from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from base.models import Ferme, User, ActiviteFerme, CultureFerme, MethodeAgricole
from base.serializers.activite import ActiviteFermeSerializer, UpdateActiviteFermeSerializer
from base.serializers.culture import CultureFermeSerializer, UpdateCultureFermeSerializer
from base.serializers.ferme import FermeViewSerializer, EmployeSerializer, UpdateFermeSerializer
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from sebania.permissions import HasResponsablePermission
from sebania.utils import db_utils
from sebania.utils.db_utils import get_one_or_raise_exception, user_is_responsable


class FermeViewSet(ViewSet):
    serializer_class = None

    @extend_schema(responses=FermeViewSerializer,
                   description="Créer un nouvel employé pour la ferme")
    @action(detail=False, methods=['post'], url_path='employes', serializer_class=EmployeSerializer,
            url_name="add-employe", permission_classes=[IsAuthenticated, HasResponsablePermission])
    def add_employe(self, request):
        ferme = get_one_or_raise_exception(Ferme, CustomException(ErrorCode.FERME_NOT_FOUND_FOR_USER, request.user.id),
                                           responsable=request.user)
        request_data = self.serializer_class(data=request.data, context={"ferme": ferme})
        request_data.is_valid(raise_exception=True)
        request_data.save()
        ferme.refresh_from_db()
        return Response(FermeViewSerializer(ferme).data, status=status.HTTP_201_CREATED)

    @extend_schema(responses=FermeViewSerializer,
                   description="Suppression d'un employé existant de la ferme")
    @action(detail=False, methods=['delete'], url_path=r'employes/(?P<user_id>\w+)', serializer_class=None,
            url_name="delete-employe", permission_classes=[IsAuthenticated, HasResponsablePermission])
    def delete_employe(self, request, user_id=None):
        ferme = get_one_or_raise_exception(Ferme, CustomException(ErrorCode.FERME_NOT_FOUND_FOR_USER, request.user.id),
                                           responsable=request.user)
        employe = get_one_or_raise_exception(User, CustomException(ErrorCode.USER_NOT_FOUND, user_id), id=user_id)
        if employe not in ferme.employes.all():
            raise CustomException(ErrorCode.USER_NOT_FOUND, user_id)
        ferme.employes.remove(employe)
        db_utils.soft_delete_employe(user_id)
        return Response(FermeViewSerializer(ferme).data, status=status.HTTP_200_OK)

    @extend_schema(description="Récupération/Modification de la liste des activités de la ferme avec regroupement par catégorie")
    @action(detail=False, methods=['get', 'put'], url_path='activites', serializer_class=UpdateActiviteFermeSerializer)
    def activites(self, request):
        ferme = db_utils.get_ferme_from_request(request)

        if request.method == 'PUT':
            if not user_is_responsable(request.user.id):
                raise CustomException(ErrorCode.USER_EMPLOYE_CANNOT_POST_FOR_RESPONSABLE)
            serializer = self.serializer_class(data=request.data, context={"ferme": ferme})
            serializer.is_valid(raise_exception=True)
            items = serializer.save()
        elif request.method == 'GET':
            items = ActiviteFerme.objects.filter(ferme=ferme).all().order_by("activite__nom")
        data = {
            "activites": items
        }
        serializer = self.serializer_class(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(description="Récupération/Modification de la liste des cultures de la ferme avec regroupement par catégorie")
    @action(detail=False, methods=['get', 'put'], url_path='cultures', serializer_class=UpdateCultureFermeSerializer)
    def cultures(self, request):
        ferme = db_utils.get_ferme_from_request(request)

        if request.method == 'PUT':
            if not user_is_responsable(request.user.id):
                raise CustomException(ErrorCode.USER_EMPLOYE_CANNOT_POST_FOR_RESPONSABLE)
            serializer = self.serializer_class(data=request.data, context={"ferme": ferme})
            serializer.is_valid(raise_exception=True)
            items = serializer.save()
        elif request.method == 'GET':
            items = CultureFerme.objects.filter(ferme=ferme).all().order_by("culture__nom")
        data = {
            "cultures": items
        }
        serializer = self.serializer_class(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(description="Récupération des informations concernant la ferme associée à l'utilisateur")
    @action(detail=False, methods=['get'], url_path='details', serializer_class=FermeViewSerializer,
            url_name="get-ferme-details")
    def get_ferme_details(self, request):
        ferme = db_utils.get_ferme_from_request(request)
        serializer = self.serializer_class(ferme)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses=FermeViewSerializer,
                   description="Modifications des informations concernant la ferme associée à l'utilisateur")
    @action(detail=False, methods=['put'], url_path='update', serializer_class=UpdateFermeSerializer,
            url_name="update-ferme-details", permission_classes=[IsAuthenticated, HasResponsablePermission])
    def update_ferme_details(self, request):
        ferme = get_one_or_raise_exception(Ferme, CustomException(ErrorCode.FERME_NOT_FOUND_FOR_USER, request.user.id),
                                           responsable=request.user)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        ferme.nom = serializer.validated_data["nom"]
        ferme.adresse = serializer.validated_data["adresse"]
        ferme.superficie_cultivee = serializer.validated_data["superficie_cultivee"]
        ferme.code_postal = serializer.validated_data["code_postal"]
        methodes_agricoles = MethodeAgricole.objects.filter(id__in=serializer.validated_data["methodes_agricoles"])
        ferme.methodes_agricoles.set(methodes_agricoles)
        ferme.save()
        return Response(FermeViewSerializer(ferme).data, status=status.HTTP_200_OK)
