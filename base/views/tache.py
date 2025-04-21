from collections import defaultdict

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from base.filters.tache import TacheFilter, TacheCalendrierFilter
from base.models import Tache
from base.models.statut import StatutTache
from base.serializers.tache import TacheSerializer, CalendrierSerializer
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
                   )
    @action(detail=False, methods=['get'], url_path='calendrier', serializer_class=CalendrierSerializer)
    def calendrier(self, request):
        ferme = get_ferme_for_user(request)
        queryset = Tache.objects.filter(ferme=ferme)

        filtre = TacheCalendrierFilter(request.GET, queryset=queryset)
        if not filtre.is_valid():
            return Response(filtre.errors, status=status.HTTP_400_BAD_REQUEST)

        # Grouper les tâches par jour
        taches_par_jour = defaultdict(list)
        total_global = 0

        for tache in filtre.qs:
            jour = tache.date.strftime("%d/%m/%Y")
            taches_par_jour[jour].append(tache)

        jours = []
        for jour, taches in sorted(taches_par_jour.items()):
            total_jour = sum(t.duree_minutes for t in taches)
            statut_jour = StatutTache.from_statuts(tache.get_statut() for tache in taches).name

            jours.append({
                'jour': jour,
                'total_jour': total_jour,
                'statut': statut_jour
            })
            total_global += total_jour

        # Statut global : le pire statut de tous les jours
        statut_global = StatutTache.from_statut_names(j['statut'] for j in jours).name

        calendrier_data = {
            'jours': jours,
            'total': total_global,
            'statut': statut_global
        }

        serializer = self.get_serializer(calendrier_data)
        return Response(serializer.data)
