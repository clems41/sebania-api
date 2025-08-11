import datetime

from django.db.models import Q

def apply_common_filters_dashboard(queryset, params, skip_parcelle: bool):
    date_debut = params.get('date_debut')
    date_fin = params.get('date_fin')
    culture_id = params.get('culture_id')
    activite_id = params.get('activite_id')
    parcelle_id = params.get('parcelle_id')

    if date_debut and date_fin:
        date_debut_formatted = datetime.datetime.strptime(date_debut, "%d/%m/%Y").date()
        date_fin_formatted = datetime.datetime.strptime(date_fin, "%d/%m/%Y").date()
        queryset = queryset.filter(date__range=[date_debut_formatted, date_fin_formatted])

    if culture_id:
        queryset = queryset.filter(cultures__culture_id=culture_id)

    if activite_id:
        queryset = queryset.filter(activite_id=activite_id)

    if parcelle_id and not skip_parcelle:
        queryset = queryset.filter(
            Q(parcelles__id=parcelle_id) |
            Q(cultures__parcelles__id=parcelle_id)
        )

    return queryset.distinct()
