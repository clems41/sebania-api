from django.urls import reverse
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from base.models import Ferme, User, ActiviteFerme, CultureFerme
from base.serializers.activite import ActiviteFermeSerializer
from base.serializers.culture import CultureFermeSerializer
from base.serializers.ferme import FermeViewSerializer, EmployeSerializer
from sebania.permissions import HasResponsablePermission
from sebania.services import http_service


class FermeViewSet(ViewSet):
    serializer_class = None

    @extend_schema(responses=FermeViewSerializer,
                   description="Créer un nouvel employé pour la ferme")
    @action(detail=False, methods=['post'], url_path='employes', serializer_class=EmployeSerializer,
            url_name="add-employe", permission_classes=[IsAuthenticated, HasResponsablePermission])
    def add_employe(self, request):
        ferme = get_object_or_404(Ferme, responsable=request.user)
        request_data = self.serializer_class(data=request.data, context={"ferme": ferme})
        request_data.is_valid(raise_exception=True)
        request_data.save()
        ferme.refresh_from_db()
        return Response(FermeViewSerializer(ferme).data, status=status.HTTP_201_CREATED)

    @extend_schema(responses=FermeViewSerializer,
                   description="Suppression d'un employé existant de la ferme")
    @action(detail=False, methods=['delete'], url_path='employes/(?P<user_id>\w+)', serializer_class=None,
            url_name="delete-employe", permission_classes=[IsAuthenticated, HasResponsablePermission])
    def delete_employe(self, request, user_id = None):
        ferme = get_object_or_404(Ferme, responsable=request.user)
        employe = get_object_or_404(User, id=user_id)
        if employe not in ferme.employes.all():
            return Response({"detail": "Cet employé n'a pas été trouvé pour votre ferme.'"}, status=status.HTTP_404_NOT_FOUND)
        ferme.employes.remove(employe)
        return Response(FermeViewSerializer(ferme).data, status=status.HTTP_200_OK)

    @extend_schema(responses=ActiviteFermeSerializer(many=True),
        description="Récupération de la liste des activités de la ferme par catégorie")
    @action(detail=False, methods=['get'], url_path='activites', serializer_class=ActiviteFermeSerializer,
            url_name="get-activites")
    def get_activites(self, request):
        ferme = http_service.get_ferme_for_user(request)
        items = ActiviteFerme.objects.filter(ferme=ferme).all().order_by("categorie", "activite__nom")
        serializer = self.serializer_class(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses=CultureFermeSerializer(many=True),
                   description="Récupération de la liste des cultures de la ferme par catégorie")
    @action(detail=False, methods=['get'], url_path='cultures', serializer_class=CultureFermeSerializer,
            url_name="get-cultures")
    def get_cultures(self, request):
        ferme = http_service.get_ferme_for_user(request)
        items = CultureFerme.objects.filter(ferme=ferme).all().order_by("categorie", "culture__nom")
        serializer = self.serializer_class(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)