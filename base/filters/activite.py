import django_filters
from jsonschema.exceptions import ValidationError
from django.db.models import Q

from base.models import Activite
from sebania.exceptions.activite import ActiviteQueryTooShortException


class ActiviteFilter(django_filters.FilterSet):
    query = django_filters.CharFilter(method='filter_by_query')
    class Meta:
        model = Activite
        fields = {}

    def filter_by_query(self, queryset, name, value):
        if len(value.strip()) < 3:
            raise ActiviteQueryTooShortException(value)

        return queryset.filter(
            Q(nom__icontains=value) | Q(mots_cles__icontains=value)
        )