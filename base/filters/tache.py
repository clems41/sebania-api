import django_filters

from base.models import Tache, User
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
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
            raise CustomException(ErrorCode.TACHE_CALENDRIER_USERID_OBLIGATOIRE)
        db_utils.get_one_or_raise_exception(User, CustomException(ErrorCode.USER_NOT_FOUND, user_id), id=user_id)
        if (semaine and mois) or (not semaine and not mois):
            raise CustomException(ErrorCode.TACHE_CALENDRIER_FILTRE_INCORRECT, semaine=semaine, mois=mois)
        if not annee:
            raise CustomException(ErrorCode.TACHE_CALENDRIER_ANNEE_OBLIGATOIRE)

    def filter_queryset(self, queryset):
        self.clean_query()
        return super().filter_queryset(queryset)

    def filter_by_semaine(self, queryset, name, value):
        return queryset.extra(where=["EXTRACT(WEEK FROM date) = %s"], params=[value])

    def filter_by_mois(self, queryset, name, value):
        return queryset.extra(where=["EXTRACT(MONTH FROM date) = %s"], params=[value])

    def filter_by_annee(self, queryset, name, value):
        return queryset.extra(where=["EXTRACT(YEAR FROM date) = %s"], params=[value])