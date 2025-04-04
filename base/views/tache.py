from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet

from base.filters.tache import TacheFilter
from base.models import Tache
from base.serializers.tache import TacheSerializer
from sebania.exceptions.auth import EmployeCannotActForResponsableException
from sebania.utils import db_utils
from sebania.utils.db_utils import get_ferme_for_user


class TacheModelViewSet(ModelViewSet):
    serializer_class = TacheSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TacheFilter

    def get_queryset(self):
        ferme = get_ferme_for_user(self.request)
        return Tache.objects.filter(ferme=ferme).all()

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        if db_utils.user_is_employe(user.id):
            tache = self.get_object()
            if tache.user_id != user.id:
                raise EmployeCannotActForResponsableException()
        return super(TacheModelViewSet, self).destroy(request, *args, **kwargs)