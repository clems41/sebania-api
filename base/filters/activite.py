import django_filters
from django.db.models import Q

from base.models import Activite
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode


class ActiviteFilter(django_filters.FilterSet):
    query = django_filters.CharFilter(method='filter_by_query')
    class Meta:
        model = Activite
        fields = {}

    def filter_by_query(self, queryset, name, value):
        if len(value.strip()) < 3:
            raise CustomException(ErrorCode.ACTIVITE_QUERY_TOO_SHORT, len(value.strip()))
        query_split = value.strip().split(' ')
        filters = Q()
        for query in query_split:
            filters |= Q(nom__icontains=query) | Q(mots_cles__icontains=query)
        return queryset.filter(filters)