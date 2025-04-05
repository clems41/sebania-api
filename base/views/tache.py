from django.db.models import Sum
from django.db.models.functions import TruncDate
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from base.filters.tache import TacheFilter, TacheCalendrierFilter
from base.models import Tache
from base.models.statut import StatutTotal
from base.serializers.ferme import FermeViewSerializer
from base.serializers.tache import TacheSerializer, CalendrierSerializer
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

        # On groupe par jour et somme les durées
        data = (
            filtre.qs
            .annotate(jour=TruncDate('date'))  # Troncature de la date pour grouper par jour
            .values('jour')  # Grouper par jour
            .annotate(total_jour=Sum('duree_minutes'))  # Somme des durées par jour
            .order_by('jour')
        )

        # Maintenant, préparer les jours et le statut
        jours = []
        total_global = 0
        for jour in data:
            total_global += jour['total_jour']
            jours.append({
                'jour': jour['jour'],
                'total_jour': jour['total_jour'],
                'statut': StatutTotal.OK  # TODO
            })

        # Créer l'objet CalendrierSerializer
        calendrier_data = {
            'jours': jours,
            'total': total_global,
            'statut': StatutTotal.OK  # TODO
        }

        # Sérialiser et retourner la réponse
        serializer = self.get_serializer(calendrier_data)
        return Response(serializer.data)
