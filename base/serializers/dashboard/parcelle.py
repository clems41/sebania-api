from django.db.models import Sum
from rest_framework import serializers

from base.filters.dashboard import apply_common_filters_dashboard
from base.models import Tache


class ParcellesDashboardSerializer(serializers.Serializer):
    parcelle_nom = serializers.CharField()
    duree_minutes = serializers.IntegerField()

    @classmethod
    def get_data(cls, ferme, params):
        base_qs = Tache.objects.select_related('ferme', 'activite') \
            .prefetch_related('cultures', 'parcelles') \
            .filter(ferme=ferme)

        base_qs = apply_common_filters_dashboard(base_qs, params, False)

        qs = (base_qs
              .values('parcelles__nom')
              .annotate(duree_minutes=Sum('duree_minutes'))
              .order_by())

        return [
            {'parcelle_nom': row['parcelles__nom'], 'duree_minutes': row['duree_minutes'] or 0}
            for row in qs if row['parcelles__nom']
        ]
