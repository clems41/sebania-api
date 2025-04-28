import calendar
from collections import defaultdict
import datetime

from rest_framework import serializers

from base.filters.tache import TacheCalendrierFilter
from base.models import Tache, Ferme
from base.models.statut import StatutJour
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from sebania.utils.db_utils import get_ferme_for_user


class CalendrierJourSerializer(serializers.Serializer):
    jour = serializers.DateField(format="%d/%m/%Y", input_formats=['%d/%m/%Y'])
    total_jour_minutes = serializers.IntegerField()
    nb_taches_with_missing_fields = serializers.IntegerField()
    statut = serializers.ChoiceField(choices=[tag.name for tag in StatutJour])


class CalendrierSerializer(serializers.Serializer):
    jours = CalendrierJourSerializer(many=True)
    total_minutes = serializers.IntegerField()

    def __init__(self, request, *args, **kwargs):
        calendrier_data = self._get_calendrier_data(request)
        super(CalendrierSerializer, self).__init__(calendrier_data)

    def _get_calendrier_data(self, request):
        ferme = get_ferme_for_user(request)
        queryset = Tache.objects.filter(ferme=ferme)

        filtres = TacheCalendrierFilter(request.GET, queryset=queryset)
        if not filtres.is_valid():
            raise CustomException(ErrorCode.TACHE_CALENDRIER_FILTRE_INCORRECT)

        # Grouper les tâches par jour
        taches = filtres.qs
        taches_par_jour = self._init_taches_par_jour(filtres)
        total_global = 0

        for tache in taches:
            jour = tache.date.strftime("%d/%m/%Y")
            taches_par_jour[jour].append(tache)

        jours = []
        for jour, taches in sorted(taches_par_jour.items()):
            total_jour_minutes = sum(t.duree_minutes for t in taches)
            statut_jour = StatutJour.from_total_jour(total_jour_minutes).name
            nb_taches_with_missing_fields = sum(1 for t in taches if t.get_fields_are_missing())

            jours.append({
                'jour': jour,
                'total_jour_minutes': total_jour_minutes,
                'statut': statut_jour,
                'nb_taches_with_missing_fields': nb_taches_with_missing_fields
            })
            total_global += total_jour_minutes

        return {
            'jours': jours,
            'total_minutes': total_global,
        }

    def _init_taches_par_jour(self, filtres: TacheCalendrierFilter):
        taches_par_jour = defaultdict(list)
        semaine = filtres.form.cleaned_data.get('semaine')
        mois = filtres.form.cleaned_data.get('mois')
        annee = int(filtres.form.cleaned_data.get('annee'))
        # Même s'il n'y a pas de tâche pour un jour donné, il doit tout de même être présent dans la liste.
        if semaine is not None:
            semaine = int(semaine)
            day_range = range(1, 8)
            for day in day_range:
                date = datetime.date.fromisocalendar(annee, semaine, day)
                date_formatted = date.strftime("%d/%m/%Y")
                taches_par_jour[date_formatted] = []
        elif mois is not None:
            mois = int(mois)
            _, nb_jours = calendar.monthrange(annee, mois)
            day_range = range(1, nb_jours + 1)
            for day in day_range:
                date = datetime.date(annee, mois, day)
                date_formatted = date.strftime("%d/%m/%Y")
                taches_par_jour[date_formatted] = []
        return taches_par_jour
