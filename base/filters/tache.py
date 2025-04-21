import django_filters
from rest_framework.exceptions import ValidationError

from base.models import Tache, User
from sebania.exceptions.tache import TacheCalendrierFiltreIncorrectException, \
    TacheCalendrierFiltreAnneeObligatoireException, TacheCalendrierFiltreUserIdObligatoireException
from sebania.exceptions.user import UserNotFoundException
from sebania.utils import db_utils


class TacheFilter(django_filters.FilterSet):
    class Meta:
        model = Tache
        fields = {
            'user_id': ['exact'],
            'date': ['exact'],
        }


class TacheCalendrierFilter(django_filters.FilterSet):
    semaine = django_filters.NumberFilter(method='filter_by_semaine')
    mois = django_filters.NumberFilter(method='filter_by_mois')
    annee = django_filters.NumberFilter(method='filter_by_annee')

    class Meta:
        model = Tache
        fields = {
            'user_id': ['exact'],
        }

    def clean_query(self):
        semaine = self.data.get('semaine')
        mois = self.data.get('mois')
        annee = self.data.get('annee')
        user_id = self.data.get('user_id')
        if not user_id:
            raise TacheCalendrierFiltreUserIdObligatoireException()
        db_utils.get_one_or_raise_exception(User, UserNotFoundException(user_id), id=user_id)
        if (semaine and mois) or (not semaine and not mois):
            raise TacheCalendrierFiltreIncorrectException(semaine, mois)
        if not annee:
            raise TacheCalendrierFiltreAnneeObligatoireException()

    def filter_queryset(self, queryset):
        self.clean_query()
        return super().filter_queryset(queryset)

    def filter_by_semaine(self, queryset, name, value):
        return queryset.extra(where=["EXTRACT(WEEK FROM date) = %s"], params=[value])

    def filter_by_mois(self, queryset, name, value):
        return queryset.extra(where=["EXTRACT(MONTH FROM date) = %s"], params=[value])

    def filter_by_annee(self, queryset, name, value):
        return queryset.extra(where=["EXTRACT(YEAR FROM date) = %s"], params=[value])