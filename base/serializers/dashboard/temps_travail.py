from django.db.models import Sum, Avg, Count
from rest_framework import serializers

from base.filters.dashboard import apply_common_filters_dashboard
from base.models import Tache, Activite, Culture, Parcelle
from base.serializers.activite import ActiviteSerializer
from base.serializers.culture import CultureSerializer
from base.serializers.parcelle import ParcelleSerializer
from sebania.utils.db_utils import get_one_or_none


class DureeParJourDashboardSerializer(serializers.Serializer):
    date = serializers.DateField()
    duree_minutes = serializers.IntegerField()
    moyenne_duree_minutes = serializers.FloatField()

    @classmethod
    def get_data(cls, ferme, params):
        base_qs = Tache.objects.select_related('ferme', 'activite') \
            .prefetch_related('cultures', 'parcelles') \
            .filter(ferme=ferme)

        base_qs = apply_common_filters_dashboard(base_qs, params)

        qs = (base_qs
              .values('date')
              .annotate(duree_minutes=Sum('duree_minutes'))
              .order_by('date'))

        avg_qs = (Tache.objects
                  .values('date')
                  .annotate(moyenne_duree_minutes=Avg('duree_minutes')))
        avg_map = {x['date']: x['moyenne_duree_minutes'] for x in apply_common_filters_dashboard(avg_qs, params)}

        return [
            {
                'date': row['date'],
                'duree_minutes': row['duree_minutes'] or 0,
                'moyenne_duree_minutes': avg_map.get(row['date'], 0)
            }
            for row in qs
        ]


class TempsTravailCardsDashboardSerializer(serializers.Serializer):
    duree_minutes = serializers.IntegerField()
    moyenne_duree_minutes = serializers.FloatField()
    activite_chronophage = ActiviteSerializer()
    activite_frequente = ActiviteSerializer()
    culture_chronophage = CultureSerializer()
    culture_frequente = CultureSerializer()
    parcelle_chronophage = ParcelleSerializer()
    parcelle_frequente = ParcelleSerializer()

    @classmethod
    def get_data(cls, ferme, params):
        def top_item(qs, id_field, agg_func):
            row = (qs.values(id_field)
                   .annotate(total=agg_func('duree_minutes'))
                   .order_by('-total')
                   .first())
            if row:
                return row[id_field]
            return None

        base_qs = Tache.objects.select_related('ferme', 'activite') \
            .prefetch_related('cultures__culture', 'parcelles') \
            .filter(ferme=ferme)

        base_qs = apply_common_filters_dashboard(base_qs, params)

        duree_totale = base_qs.aggregate(total=Sum('duree_minutes'))['total'] or 0
        moyenne_totale = apply_common_filters_dashboard(Tache.objects, params).aggregate(avg=Avg('duree_minutes'))[
                             'avg'] or 0

        activite_chronophage = get_one_or_none(Activite, id=top_item(base_qs, 'activite__id', Sum))
        activite_frequente = get_one_or_none(Activite, id=top_item(base_qs, 'activite__id', Count))
        culture_chronophage = get_one_or_none(Culture,
                                              id=top_item(base_qs, 'cultures__culture__id',
                                                          Sum))
        culture_frequente = get_one_or_none(Culture,
                                            id=top_item(base_qs, 'cultures__culture__id',
                                                        Count))
        parcelle_chronophage = get_one_or_none(Parcelle, id=top_item(base_qs, 'parcelles__id', Sum))
        parcelle_frequente = get_one_or_none(Parcelle, id=top_item(base_qs, 'parcelles__id', Count))

        result = {
            'duree_minutes': duree_totale,
            'moyenne_duree_minutes': moyenne_totale,
        }
        if activite_chronophage:
            result['activite_chronophage'] = ActiviteSerializer(activite_chronophage).data
        if activite_frequente:
            result['activite_frequente'] = ActiviteSerializer(activite_frequente).data
        if culture_frequente:
            result['culture_frequente'] = CultureSerializer(culture_frequente).data
        if culture_chronophage:
            result['culture_chronophage'] = CultureSerializer(culture_chronophage).data
        if parcelle_chronophage:
            result['parcelle_chronophage'] = ParcelleSerializer(parcelle_chronophage).data
        if parcelle_frequente:
            result['parcelle_frequente'] = ParcelleSerializer(parcelle_frequente).data

        return result
