import calendar
import datetime
import json
import random
from typing import List

from django.urls import reverse_lazy
from rest_framework import status

from base.models import User, Ferme
from base.models.statut import StatutJour
from sebania.exceptions.error_code import ErrorCode
from sebania.tests import test_fixtures
from sebania.tests.SebaniaTestCase import SebaniaTestCase


class TestCalendrier(SebaniaTestCase):
    url = reverse_lazy('taches-calendrier')

    def _create_taches(self, date, ferme, user_tache: User):
        total = 0
        nb_taches_with_missing_fields = 0
        for _ in range(random.randint(5, 12)):
            duree = random.randint(30, 90)
            random_value = random.randint(1, 100)
            # création de temps à autre (8%) d'une tâche avec des champs manquants
            if random_value < 8:
                test_fixtures.create_tache(ferme=ferme, user_id=user_tache.id, duree_minutes=duree, date=date, quantite=None, unite_id=None, culture_id=None, nb_parcelles=0)
                nb_taches_with_missing_fields+=1
            else:
                test_fixtures.create_tache(ferme=ferme, user_id=user_tache.id, duree_minutes=duree, date=date)
            total += duree
        return total, nb_taches_with_missing_fields

    def _create_data(self, user_concerned: User, annee: int, numero_semaine: int = None, numero_mois: int = None, ferme: Ferme = None, missing_days=None):
        if ferme is None:
            employes = [test_fixtures.create_user(), test_fixtures.create_user(), user_concerned]
            ferme = test_fixtures.create_ferme(responsable=test_fixtures.create_user(), employes=employes)
        # Création des tâches qui matchent pour la semaine
        total = 0
        total_jour = {}
        missing_fields_jour = {}
        if numero_semaine is not None:
            for day in range(1, 8):
                date = datetime.date.fromisocalendar(annee, numero_semaine, day)
                date_formatted = date.strftime("%d/%m/%Y")
                if missing_days is not None and date_formatted in missing_days:
                    continue
                for employe in ferme.employes.all():
                    total_for_date, nb_taches_with_missing_fields = self._create_taches(date=date, ferme=ferme, user_tache=employe)
                    if user_concerned.id == employe.id:
                        total += total_for_date
                        total_jour[date_formatted] = total_for_date
                        missing_fields_jour[date_formatted] = nb_taches_with_missing_fields
        if numero_mois is not None:
            _, nb_jours = calendar.monthrange(annee, numero_mois)
            for day in range(1, nb_jours + 1):
                date = datetime.date(annee, numero_mois, day)
                date_formatted = date.strftime("%d/%m/%Y")
                if missing_days is not None and date_formatted in missing_days:
                    continue
                for employe in ferme.employes.all():
                    total_for_date, nb_taches_with_missing_fields = self._create_taches(date=date, ferme=ferme, user_tache=employe)
                    if user_concerned.id == employe.id:
                        total += total_for_date
                        total_jour[date_formatted] = total_for_date
                        missing_fields_jour[date_formatted] = nb_taches_with_missing_fields
        return total, total_jour, missing_fields_jour

    def _get_calendrier(self, annee: int = None, numero_semaine: int = None, numero_mois: int = None, user_id: int = None,
                        expected_status_code=status.HTTP_200_OK):
        # if user_id is None:
        #     user_id = self.get_current_user().id
        query_params = {}
        if annee is not None:
            query_params['annee'] = annee
        if numero_semaine is not None:
            query_params['semaine'] = numero_semaine
        if numero_mois is not None:
            query_params['mois'] = numero_mois
        if user_id is not None:
            query_params['user_id'] = user_id
        response = self.client.get(self.url, query_params, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, expected_status_code)
        return response

    def _check_response(self, response, total: int, total_jour: {}, missing_fields_jour: {}, expected_days: List[str]):
        response_data = json.loads(response.content)
        self.assertEqual(total, response_data.get("total_minutes"))
        for expected_day in expected_days:
            expected_total = total_jour.get(expected_day)
            if expected_total is None:
                expected_total = 0
            actual_day = next(
                (jour for jour in response_data.get("jours") if jour.get("jour") == expected_day),
                None)
            self.assertIsNotNone(actual_day)
            self.assertEqual(expected_total, actual_day.get("total_jour_minutes"))
            # check expected_nb_taches_with_missing_fields
            expected_nb_taches_with_missing_fields = missing_fields_jour.get(expected_day)
            if expected_nb_taches_with_missing_fields is None:
                expected_nb_taches_with_missing_fields = 0
            self.assertEqual(expected_nb_taches_with_missing_fields, actual_day.get("nb_taches_with_missing_fields"))
            self.assertEqual(StatutJour.from_total_jour(expected_total).name, actual_day.get("statut"))


    def test_calendrier_semaine(self):
        numero_semaine = 3
        total, total_jour, missing_fields_jour = self._create_data(user_concerned=self.init_current_user(), annee=2025, numero_semaine=numero_semaine)
        response = self._get_calendrier(user_id= self.get_current_user().id, annee=2025, numero_semaine=numero_semaine)
        expected_days = ["13/01/2025", "14/01/2025", "15/01/2025", "16/01/2025", "17/01/2025", "18/01/2025",
                         "19/01/2025"]
        self._check_response(response, total, total_jour, missing_fields_jour, expected_days)

    def test_calendrier_semaine_with_missing_days(self):
        numero_semaine = 3
        missing_days = ["15/01/2025", "18/01/2025"]
        total, total_jour, missing_fields_jour = self._create_data(user_concerned=self.init_current_user(), annee=2025, numero_semaine=numero_semaine, missing_days=missing_days)
        response = self._get_calendrier(user_id= self.get_current_user().id, annee=2025, numero_semaine=numero_semaine)
        expected_days = ["13/01/2025", "14/01/2025", "15/01/2025", "16/01/2025", "17/01/2025", "18/01/2025",
                         "19/01/2025"]
        self._check_response(response, total, total_jour, missing_fields_jour, expected_days)

    def test_calendrier_semaine_empty(self):
        responsable = self.init_current_user()
        test_fixtures.create_ferme(responsable=responsable)
        numero_semaine = 3
        response = self._get_calendrier(user_id= self.get_current_user().id, annee=2025, numero_semaine=numero_semaine)
        expected_days = ["13/01/2025", "14/01/2025", "15/01/2025", "16/01/2025", "17/01/2025", "18/01/2025",
                         "19/01/2025"]
        self._check_response(response, 0, {}, {}, expected_days)

    def test_calendrier_mois(self):
        numero_mois = 2
        total, total_jour, missing_fields_jour = self._create_data(user_concerned=self.init_current_user(), annee=2025, numero_mois=numero_mois)
        response = self._get_calendrier(user_id= self.get_current_user().id, annee=2025, numero_mois=numero_mois)
        expected_days = ['01/02/2025', '02/02/2025', '03/02/2025', '04/02/2025', '05/02/2025', '06/02/2025',
                         '07/02/2025', '08/02/2025', '09/02/2025', '10/02/2025', '11/02/2025', '12/02/2025',
                         '13/02/2025', '14/02/2025', '15/02/2025', '16/02/2025', '17/02/2025', '18/02/2025',
                         '19/02/2025', '20/02/2025', '21/02/2025', '22/02/2025', '23/02/2025', '24/02/2025',
                         '25/02/2025', '26/02/2025', '27/02/2025', '28/02/2025']
        self._check_response(response, total, total_jour, missing_fields_jour, expected_days)

    def test_calendrier_mois_with_missing_days(self):
        numero_mois = 2
        missing_days = ["07/02/2025", "16/02/2025", "28/02/2025"]
        total, total_jour, missing_fields_jour = self._create_data(user_concerned=self.init_current_user(), annee=2025, numero_mois=numero_mois, missing_days=missing_days)
        response = self._get_calendrier(user_id= self.get_current_user().id, annee=2025, numero_mois=numero_mois)
        expected_days = ['01/02/2025', '02/02/2025', '03/02/2025', '04/02/2025', '05/02/2025', '06/02/2025',
                         '07/02/2025', '08/02/2025', '09/02/2025', '10/02/2025', '11/02/2025', '12/02/2025',
                         '13/02/2025', '14/02/2025', '15/02/2025', '16/02/2025', '17/02/2025', '18/02/2025',
                         '19/02/2025', '20/02/2025', '21/02/2025', '22/02/2025', '23/02/2025', '24/02/2025',
                         '25/02/2025', '26/02/2025', '27/02/2025', '28/02/2025']
        self._check_response(response, total, total_jour, missing_fields_jour, expected_days)

    def test_calendrier_mois_empty(self):
        responsable = self.init_current_user()
        test_fixtures.create_ferme(responsable=responsable)
        numero_mois = 2
        response = self._get_calendrier(user_id= self.get_current_user().id, annee=2025, numero_mois=numero_mois)
        expected_days = ['01/02/2025', '02/02/2025', '03/02/2025', '04/02/2025', '05/02/2025', '06/02/2025',
                         '07/02/2025', '08/02/2025', '09/02/2025', '10/02/2025', '11/02/2025', '12/02/2025',
                         '13/02/2025', '14/02/2025', '15/02/2025', '16/02/2025', '17/02/2025', '18/02/2025',
                         '19/02/2025', '20/02/2025', '21/02/2025', '22/02/2025', '23/02/2025', '24/02/2025',
                         '25/02/2025', '26/02/2025', '27/02/2025', '28/02/2025']
        self._check_response(response, 0, {}, {}, expected_days)

    def test_calendrier_semaine_specific_user(self):
        responsable = self.init_current_user()
        employe1 = test_fixtures.create_user()
        employes = [employe1, test_fixtures.create_user()]
        ferme = test_fixtures.create_ferme(responsable=responsable, employes=employes)
        numero_semaine = 3
        total, total_jour, missing_fields_jour = self._create_data(numero_semaine=numero_semaine, annee=2025, ferme=ferme, user_concerned=employe1)
        response = self._get_calendrier(annee=2025, numero_semaine=numero_semaine, user_id=employe1.id)
        expected_days = ["13/01/2025", "14/01/2025", "15/01/2025", "16/01/2025", "17/01/2025", "18/01/2025",
                         "19/01/2025"]
        self._check_response(response, total, total_jour, missing_fields_jour, expected_days)

    def test_calendrier_mois_specific_user(self):
        responsable = test_fixtures.create_user()
        employe1 = self.init_current_user()
        employe2 = test_fixtures.create_user()
        employes = [employe1, employe2]
        ferme = test_fixtures.create_ferme(responsable=responsable, employes=employes)
        numero_mois = 2
        total, total_jour, missing_fields_jour = self._create_data(annee=2025, numero_mois=numero_mois, ferme=ferme, user_concerned=employe2)
        response = self._get_calendrier(annee=2025, numero_mois=numero_mois, user_id=employe2.id)
        expected_days = ['01/02/2025', '02/02/2025', '03/02/2025', '04/02/2025', '05/02/2025', '06/02/2025',
                         '07/02/2025', '08/02/2025', '09/02/2025', '10/02/2025', '11/02/2025', '12/02/2025',
                         '13/02/2025', '14/02/2025', '15/02/2025', '16/02/2025', '17/02/2025', '18/02/2025',
                         '19/02/2025', '20/02/2025', '21/02/2025', '22/02/2025', '23/02/2025', '24/02/2025',
                         '25/02/2025', '26/02/2025', '27/02/2025', '28/02/2025']
        self._check_response(response, total, total_jour, missing_fields_jour, expected_days)

    def test_calendrier_nok_semaine_et_mois(self):
        responsable = self.init_current_user()
        test_fixtures.create_ferme(responsable=responsable)
        response = self._get_calendrier(annee=2025, numero_semaine=3, numero_mois=3, expected_status_code=status.HTTP_400_BAD_REQUEST, user_id=responsable.id)
        self.check_error_response(response, expected_error=ErrorCode.TACHE_CALENDRIER_FILTRE_INCORRECT, semaine=3, mois=3)

    def test_calendrier_nok_annee(self):
        responsable = self.init_current_user()
        test_fixtures.create_ferme(responsable=responsable)
        response = self._get_calendrier(numero_semaine=3, expected_status_code=status.HTTP_400_BAD_REQUEST, user_id=responsable.id)
        self.check_error_response(response, expected_error=ErrorCode.TACHE_CALENDRIER_ANNEE_OBLIGATOIRE)

    def test_calendrier_nok_userid(self):
        responsable = self.init_current_user()
        test_fixtures.create_ferme(responsable=responsable)
        response = self._get_calendrier(annee=2025, numero_semaine=3, expected_status_code=status.HTTP_400_BAD_REQUEST)
        self.check_error_response(response, expected_error=ErrorCode.TACHE_CALENDRIER_USERID_OBLIGATOIRE)