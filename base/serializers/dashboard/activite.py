from rest_framework import serializers
from django.db.models import Sum, Avg

from base.filters.dashboard import apply_common_filters_dashboard
from base.models import Tache


class ActivitesDashboardSerializer(serializers.Serializer):
    categorie_nom = serializers.CharField()
    duree_minutes = serializers.IntegerField()
    moyenne_duree_minutes = serializers.FloatField()

    @classmethod
    def get_data(cls, ferme, params):
        base_qs = Tache.objects.select_related('activite', 'ferme') \
            .prefetch_related('cultures', 'parcelles') \
            .filter(ferme=ferme)

        base_qs = apply_common_filters_dashboard(base_qs, params)

        qs = (base_qs
              .values('activite__activiteferme__categorie')
              .annotate(duree_minutes=Sum('duree_minutes'))
              .order_by())

        avg_qs = (Tache.objects
                  .values('activite__activiteferme__categorie')
                  .annotate(moyenne_duree_minutes=Avg('duree_minutes')))
        avg_map = {x['activite__activiteferme__categorie']: x['moyenne_duree_minutes'] for x in
                   apply_common_filters_dashboard(avg_qs, params)}

        return [
            {
                'categorie_nom': row['activite__activiteferme__categorie'],
                'duree_minutes': row['duree_minutes'] or 0,
                'moyenne_duree_minutes': avg_map.get(row['activite__activiteferme__categorie'], 0)
            }
            for row in qs
        ]
