from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from base.models import Parcelle
from base.serializers.parcelle import ParcelleSerializer
from sebania.permissions import HasResponsablePermission
from sebania.utils.db_utils import get_ferme_for_user


class ParcelleModelViewSet(ModelViewSet):
    serializer_class = ParcelleSerializer

    def get_queryset(self):
        ferme = get_ferme_for_user(self.request)
        return Parcelle.objects.filter(ferme=ferme).all()

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), HasResponsablePermission()]
        else:
            return [IsAuthenticated()]