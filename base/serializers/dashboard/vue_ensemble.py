from collections import defaultdict
from datetime import datetime, date

from django.db.models import Sum, Q
from django.db.models.functions import TruncDate, TruncMonth
from rest_framework import serializers

from base.models import Ferme, Tache, Activite, Culture
from base.serializers.activite import ActiviteSerializer
from base.serializers.culture import CultureSerializer


class VueEnsembleCardsSerializer(serializers.Serializer):
    temps_travail_mois_actuel_en_minutes = serializers.IntegerField(read_only=True)
    temps_travail_mois_annee_precedente_en_minutes = serializers.IntegerField(read_only=True)
    temps_travail_moyen_par_jour_en_minutes = serializers.IntegerField(read_only=True)
    temps_travail_moyen_par_mois_en_minutes = serializers.IntegerField(read_only=True)
    activite_chronophage = ActiviteSerializer(read_only=True)
    culture_chronophage = CultureSerializer(read_only=True)
    pourcentage_activite = serializers.IntegerField(read_only=True)
    pourcentage_culture = serializers.IntegerField(read_only=True)

    def __init__(self, ferme: Ferme):
        current_month = datetime.today().month
        current_year = datetime.today().year
        stats = Tache.objects.filter(ferme=ferme).aggregate(
            temps_travail_mois_actuel_en_minutes=Sum('duree_minutes',
                                                     filter=Q(date__month=current_month, date__year=current_year)),
            temps_travail_mois_annee_precedente_en_minutes=Sum('duree_minutes', filter=Q(date__month=current_month,
                                                                                         date__year=current_year - 1)),
        )
        stats['temps_travail_moyen_par_jour_en_minutes'] = self._get_temps_travail_moyen_par_jour_en_minutes(ferme)
        stats['temps_travail_moyen_par_mois_en_minutes'] = self._get_temps_travail_moyen_par_mois_en_minutes(ferme)
        activite_chronophage = self._get_activite_chronophage(ferme)
        culture_chronophage = self._get_culture_chronophage(ferme)
        total_duration = self._get_total_duration(ferme)
        stats['activite_chronophage'] = ActiviteSerializer(
            Activite.objects.get(id=activite_chronophage['activite_id'])).data
        stats['pourcentage_activite'] = activite_chronophage['total_duration'] / total_duration * 100
        stats['culture_chronophage'] = CultureSerializer(Culture.objects.get(id=culture_chronophage['culture_id'])).data
        stats['pourcentage_culture'] = culture_chronophage['total_duration'] / total_duration * 100
        super().__init__(stats)

    def _get_temps_travail_moyen_par_jour_en_minutes(self, ferme: Ferme):
        start_of_year = date.today().replace(month=1, day=1)

        # Étape 1–3 : grouper par jour et sommer les durées
        daily_totals = (
            Tache.objects
            .filter(date__gte=start_of_year, ferme=ferme)
            .annotate(day=TruncDate('date'))
            .values('day')
            .annotate(total_duration=Sum('duree_minutes'))  # en minutes
        )

        # Étape 4 : calcul de la moyenne
        # On récupère les totaux et on calcule la moyenne en Python
        total_durations = [entry['total_duration'] for entry in daily_totals]
        if total_durations:
            avg_per_day = sum(total_durations) / len(total_durations)
        else:
            avg_per_day = 0
        return avg_per_day

    def _get_temps_travail_moyen_par_mois_en_minutes(self, ferme: Ferme):
        start_of_year = date.today().replace(month=1, day=1)

        # Étape 1–3 : grouper par jour et sommer les durées
        monthly_totals = (
            Tache.objects
            .filter(date__gte=start_of_year, ferme=ferme)
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(total_duration=Sum('duree_minutes'))  # en minutes
        )

        # Étape 4 : calcul de la moyenne
        # On récupère les totaux et on calcule la moyenne en Python
        total_durations = [entry['total_duration'] for entry in monthly_totals]
        if total_durations:
            avg_per_day = sum(total_durations) / len(total_durations)
        else:
            avg_per_day = 0
        return avg_per_day

    def _get_activite_chronophage(self, ferme: Ferme):
        start_of_year = date.today().replace(month=1, day=1)

        # Étape 1–3 : grouper par activité et sommer les durées
        return (
            Tache.objects
            .filter(date__gte=start_of_year, ferme=ferme)
            .values('activite_id')
            .annotate(total_duration=Sum('duree_minutes'))
            .order_by('-total_duration')
            .first()
        )

    def _get_culture_chronophage(self, ferme: Ferme):
        start_of_year = date.today().replace(month=1, day=1)

        # Toutes les activités depuis le début de l’année
        taches = Tache.objects.filter(date__gte=start_of_year, ferme=ferme).prefetch_related('cultures')

        # Dictionnaire pour accumuler les durées par culture
        durees_par_culture = defaultdict(float)

        for tache in taches:
            cultures = list(tache.cultures.all())
            if not cultures:
                continue
            part_par_culture = tache.duree_minutes / len(cultures)
            for culture in cultures:
                durees_par_culture[culture.culture.id] += part_par_culture

        # Trouver la culture avec le temps total maximum
        if durees_par_culture:
            culture_id_max = max(durees_par_culture, key=durees_par_culture.get)
            return {'culture_id': culture_id_max, 'total_duration': durees_par_culture[culture_id_max]}
        else:
            return {'culture_id': None, 'total_duration': 0}

    def _get_total_duration(self, ferme: Ferme):
        start_of_year = date.today().replace(month=1, day=1)

        return Tache.objects.filter(date__gte=start_of_year, ferme=ferme).aggregate(
            total=Sum('duree_minutes')
        )['total'] or 0
