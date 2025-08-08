from django.db.models import Q

def apply_common_filters_dashboard(queryset, params):
    date_debut = params.get('date_debut')
    date_fin = params.get('date_fin')
    culture_id = params.get('culture_id')
    activite_id = params.get('activite_id')
    parcelle_id = params.get('parcelle_id')

    if date_debut and date_fin:
        queryset = queryset.filter(date__range=[date_debut, date_fin])

    if culture_id:
        queryset = queryset.filter(cultures__culture_id=culture_id)

    if activite_id:
        queryset = queryset.filter(activite_id=activite_id)

    if parcelle_id:
        queryset = queryset.filter(
            Q(parcelles__id=parcelle_id) |
            Q(cultures__parcelles__id=parcelle_id)
        )

    return queryset.distinct()
