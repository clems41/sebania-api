from django.db.models import Sum, Avg
from rest_framework import serializers

from base.filters.dashboard import apply_common_filters_dashboard
from base.models import Tache


class CulturesDashboardSerializer(serializers.Serializer):
    culture_nom = serializers.CharField()
    duree_minutes = serializers.IntegerField()
    moyenne_duree_minutes = serializers.FloatField()

    @classmethod
    def get_data(cls, ferme, params):
        base_qs = Tache.objects.select_related('ferme', 'activite') \
            .prefetch_related('cultures__culture', 'cultures__parcelles', 'parcelles') \
            .filter(ferme=ferme)

        base_qs = apply_common_filters_dashboard(base_qs, params)

        qs = (base_qs
              .values('cultures__culture__nom')
              .annotate(duree_minutes=Sum('duree_minutes'))
              .order_by())

        avg_qs = (Tache.objects
                  .values('cultures__culture__nom')
                  .annotate(moyenne_duree_minutes=Avg('duree_minutes')))
        avg_map = {x['cultures__culture__nom']: x['moyenne_duree_minutes'] for x in apply_common_filters_dashboard(avg_qs, params)}

        return [
            {
                'culture_nom': row['cultures__culture__nom'],
                'duree_minutes': row['duree_minutes'] or 0,
                'moyenne_duree_minutes': avg_map.get(row['cultures__culture__nom'], 0)
            }
            for row in qs if row['cultures__culture__nom']
        ]
