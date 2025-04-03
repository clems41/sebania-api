from rest_framework.viewsets import ModelViewSet

from base.models import Tache
from base.serializers.tache import TacheSerializer
from sebania.utils.db_utils import get_ferme_for_user


class TacheModelViewSet(ModelViewSet):
    serializer_class = TacheSerializer

    def get_queryset(self):
        ferme = get_ferme_for_user(self.request)
        return Tache.objects.filter(ferme=ferme).all()