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
    semaine = django_filters.NumberFilter(method='filter_by_semaine', required=False)
    mois = django_filters.NumberFilter(method='filter_by_mois', required=False)
    annee = django_filters.NumberFilter(method='filter_by_annee')

    class Meta:
        model = Tache
        fields = {
            'user_id': ['exact'],
        }

    def is_valid(self, raise_exception=False):
        semaine = self.data.get('semaine')
        mois = self.data.get('mois')
        annee = self.data.get('annee')
        user_id = self.data.get('user_id')
        if not user_id:
            if raise_exception:
                raise CustomException(ErrorCode.TACHE_CALENDRIER_USERID_OBLIGATOIRE)
            else:
                return False
        db_utils.get_one_or_raise_exception(User, CustomException(ErrorCode.USER_NOT_FOUND, user_id), id=user_id)
        if (semaine and mois) or (not semaine and not mois):
            if raise_exception:
                raise CustomException(ErrorCode.TACHE_CALENDRIER_FILTRE_INCORRECT, semaine=semaine, mois=mois)
            else:
                return False
        if not annee:
            if raise_exception:
                raise CustomException(ErrorCode.TACHE_CALENDRIER_ANNEE_OBLIGATOIRE)
            else:
                return False
        return True

    def filter_by_semaine(self, queryset, name, value):
        return queryset.extra(where=["EXTRACT(WEEK FROM date) = %s"], params=[value])

    def filter_by_mois(self, queryset, name, value):
        return queryset.extra(where=["EXTRACT(MONTH FROM date) = %s"], params=[value])

    def filter_by_annee(self, queryset, name, value):
        return queryset.extra(where=["EXTRACT(YEAR FROM date) = %s"], params=[value])