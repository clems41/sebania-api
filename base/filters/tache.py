import django_filters

from base.models import Tache


class TacheFilter(django_filters.FilterSet):
    class Meta:
        model = Tache
        fields = {
            'user_id': ['exact'],
            'date': ['exact'],
        }