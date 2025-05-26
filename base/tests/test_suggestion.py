import datetime
import json
from datetime import timedelta

from django.urls import reverse_lazy
from django.utils import timezone
from rest_framework import status

from sebania.tests import test_fixtures
from sebania.tests.SebaniaTestCase import SebaniaTestCase


class TestSuggestionParcelles(SebaniaTestCase):
    url = reverse_lazy('suggestions-get-parcelles')
    parcelles = None
    ferme = None
    user = None

    def setUp(self):
        self.user = self.init_current_user()
        self.ferme = test_fixtures.create_ferme(responsable=self.user)
        self.parcelles = []
        for _ in range(20):
            parcelle = test_fixtures.create_parcelle(self.ferme)
            self.parcelles.append(parcelle)

    def _get_suggestions_and_check_response(self, culture_id: int, activite_id: int, expected_status_code: int, expected_parcelle_ids):
        response = self.client.get(self.url, query_params={'culture_id': culture_id, 'activite_id': activite_id}, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, expected_status_code)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data), len(expected_parcelle_ids))
        for expected_parcelle_id in expected_parcelle_ids:
            actual_parcelle = next((parcelle for parcelle in response_data if parcelle.get("id") == expected_parcelle_id), None)
            self.assertIsNotNone(actual_parcelle, "La parcelle id={} n'a pas été trouvée dans la réponse".format(expected_parcelle_id))

    def test_no_suggestion(self):
        expected_parcelle_ids = []
        self._get_suggestions_and_check_response(culture_id=1, activite_id=2, expected_status_code=status.HTTP_200_OK, expected_parcelle_ids=expected_parcelle_ids)

    def test_une_parcelle(self):
        culture_id = 1
        parcelle = self.parcelles[8]
        test_fixtures.create_tache(culture_ids=[8, culture_id, 5], parcelle_ids=[parcelle.id], activite_id=8, user_id=self.user.id, ferme=self.ferme)
        expected_parcelle_ids = [parcelle.id]
        self._get_suggestions_and_check_response(culture_id=culture_id, activite_id=4, expected_status_code=status.HTTP_200_OK, expected_parcelle_ids=expected_parcelle_ids)

    def test_plusieurs_parcelles(self):
        culture_id = 1
        parcelle_ids = [self.parcelles[2].id, self.parcelles[5].id, self.parcelles[9].id]
        test_fixtures.create_tache(culture_ids=[8, culture_id, 5], parcelle_ids=parcelle_ids, activite_id=8, user_id=self.user.id, ferme=self.ferme)
        expected_parcelle_ids = parcelle_ids
        self._get_suggestions_and_check_response(culture_id=culture_id, activite_id=4, expected_status_code=status.HTTP_200_OK, expected_parcelle_ids=expected_parcelle_ids)

    def test_plantation(self):
        culture_id = 12
        parcelle_ids = [self.parcelles[2].id, self.parcelles[5].id, self.parcelles[9].id]
        test_fixtures.create_tache(culture_ids=[8, culture_id, 5], parcelle_ids=parcelle_ids, activite_id=8, user_id=self.user.id, ferme=self.ferme)
        expected_parcelle_ids = []
        self._get_suggestions_and_check_response(culture_id=culture_id, activite_id=8, expected_status_code=status.HTTP_200_OK, expected_parcelle_ids=expected_parcelle_ids)

    def test_semis_direct(self):
        culture_id = 12
        parcelle_ids = [self.parcelles[2].id, self.parcelles[5].id, self.parcelles[9].id]
        test_fixtures.create_tache(culture_ids=[8, culture_id, 5], parcelle_ids=parcelle_ids, activite_id=8, user_id=self.user.id, ferme=self.ferme)
        expected_parcelle_ids = []
        self._get_suggestions_and_check_response(culture_id=culture_id, activite_id=7, expected_status_code=status.HTTP_200_OK, expected_parcelle_ids=expected_parcelle_ids)

    def test_recolte_avant_implantation(self):
        culture_id = 1
        nouvelle_parcelle = self.parcelles[8]
        ancienne_parcelle = self.parcelles[12]
        ancienne_date = timezone.now() - datetime.timedelta(days=30)
        nouvelle_date = timezone.now() - datetime.timedelta(days=15)
        test_fixtures.create_tache(culture_ids=[culture_id], parcelle_ids=[ancienne_parcelle.id], activite_id=17, user_id=self.user.id, ferme=self.ferme, date=ancienne_date) # recolte sur ancienne parceller
        test_fixtures.create_tache(culture_ids=[culture_id], parcelle_ids=[nouvelle_parcelle.id], activite_id=8, user_id=self.user.id, ferme=self.ferme, date=nouvelle_date) # plantation sur nouvelle parcelle
        expected_parcelle_ids = [nouvelle_parcelle.id]
        self._get_suggestions_and_check_response(culture_id=culture_id, activite_id=4, expected_status_code=status.HTTP_200_OK, expected_parcelle_ids=expected_parcelle_ids)

