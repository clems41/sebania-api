from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from base.filters.tache import TacheFilter
from base.models import Tache
from base.serializers.calendrier import CalendrierSerializer
from base.serializers.tache import TacheSerializer
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from sebania.utils import db_utils
from sebania.utils.db_utils import get_ferme_for_user


class TacheModelViewSet(ModelViewSet):
    serializer_class = TacheSerializer
    queryset = Tache.objects.none()
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
                raise CustomException(ErrorCode.AUTH_EMPLOYE_CANNOT_POST_FOR_RESPONSABLE)
        return super(TacheModelViewSet, self).destroy(request, *args, **kwargs)

    @extend_schema(description="Récupération du total d'heures saisies par jour pour une semaine ou un mois donné",
                   parameters=[
                       OpenApiParameter("user_id", int, required=True, description="Utilisateur ayant réalisé les tâches"),
                       OpenApiParameter("annee", int, required=True, description="Année"),
                       OpenApiParameter("semaine", int, required=False, description="Numéro de semaine (1-53) ! Incompatible avec mois !"),
                       OpenApiParameter("mois", int, required=False, description="Numéro de mois (1-12) ! Incompatible avec semaine !"),
                   ],
                   responses=CalendrierSerializer
                   )
    @action(detail=False, methods=['get'], url_path='calendrier')
    def calendrier(self, request):
        serializer = CalendrierSerializer.from_request(request)
        return Response(serializer.data)
