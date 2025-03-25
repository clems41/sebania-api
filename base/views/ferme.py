from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from base.models import Ferme
from base.serializers.ferme import FermeViewSerializer, EmployeSerializer
from sebania.permissions import HasResponsablePermission


class FermeViewSet(ViewSet):
    serializer_class = None

    @extend_schema(responses=FermeViewSerializer,
                   description="Créer un nouvel employé pour la ferme")
    @action(detail=False, methods=['post'], url_path='employes', serializer_class=EmployeSerializer,
            url_name="add-employe", basename="fermes-add-employe", permission_classes=[IsAuthenticated, HasResponsablePermission])
    def add_employe(self, request):
        ferme = Ferme.objects.get(responsable=request.user)
        request_data = self.serializer_class(data=request.data, context={"ferme": ferme})
        request_data.is_valid(raise_exception=True)
        request_data.save()
        ferme.refresh_from_db()
        return Response(FermeViewSerializer(ferme).data, status=status.HTTP_201_CREATED)