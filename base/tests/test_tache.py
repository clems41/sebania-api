import datetime
import json
from copy import deepcopy
from typing import List

from django.forms import model_to_dict
from django.urls import reverse_lazy
from django.utils import timezone
from rest_framework import status

from base.models import User, Ferme, Tache, Parcelle
from base.models.tache import CultureTache
from base.tests import data
from sebania.tests import test_fixtures
from sebania.tests.SebaniaTestCase import SebaniaTestCase
from sebania.utils.db_utils import get_ferme_for_user


def _get_url_detail(tache_id: int):
    return reverse_lazy('taches-detail', args=[tache_id])


class TestTache(SebaniaTestCase):
    url = reverse_lazy('taches-list')

    def _create_or_update(self, test_data, expected_status_code, tache_id: int = None):
        test_data_copy = deepcopy(test_data)
        request = test_data_copy.get("request")
        expected_response = test_data_copy.get("expected_response")
        expected_entity = test_data_copy.get("expected_entity")
        parcelles_to_create = test_data_copy.get("parcelles_to_create", None)

        # Ajout de l'ID du user dans la requête qui diffère à chaque test
        if self.get_current_user() is None:
            self.init_current_user()
            test_fixtures.create_ferme(responsable=self.get_current_user())
        if request["user_id"] is None:
            request["user_id"] = self.get_current_user().id

        # Création des parcelles
        if parcelles_to_create is not None:
            parcelles = []
            for parcelle_nom in parcelles_to_create:
                ferme = get_ferme_for_user(self.get_current_user().id)
                parcelle = test_fixtures.create_parcelle(ferme, parcelle_nom)
                ferme.parcelle_set.add(parcelle)
                parcelles.append(parcelle)

            # Ajout de l'ID des parcelles dans la requête qui diffère à chaque test
            parcelle_ids = [parcelles[parcelle_id - 1].id if parcelle_id <= len(parcelles) else parcelle_id for
                            parcelle_id in request.get("parcelle_ids", [])]
            request["parcelle_ids"] = parcelle_ids
            for culture_tache in request.get("cultures", []):
                parcelle_ids = [parcelles[parcelle_id - 1].id if parcelle_id <= len(parcelles) else parcelle_id for
                                parcelle_id in culture_tache.get("parcelle_ids", [])]
                culture_tache["parcelle_ids"] = parcelle_ids

        # Envoi requête
        if tache_id is not None:
            response = self.client.put(_get_url_detail(tache_id), request, format='json',
                                       headers=self.get_jwt_headers())
        else:
            response = self.client.post(self.url, request, format='json', headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, expected_status_code)
        if expected_status_code <= status.HTTP_201_CREATED:
            response_data = json.loads(response.content)
            self.check_response(expected_response, response_data, request)
            tache = Tache.objects.get(id=response_data.get("id"))
            self.check_entity(expected_entity, tache, request)
        elif tache_id is None:
            # Il faut vérifier que la tâche n'a pas été créée en base (uniquement lors de la création)
            taches = Tache.objects.filter(user=self.get_current_user(),
                                          ferme=get_ferme_for_user(self.get_current_user().id)).all()
            self.assertTrue(len(taches) == 0)


class TestCreationTache(TestTache):
    def test_ok_creation_champs_manquants(self):
        self._create_or_update(data.test_ok_champs_manquants, expected_status_code=status.HTTP_201_CREATED)

    def test_ok_creation_simple(self):
        self._create_or_update(data.test_ok_simple, expected_status_code=status.HTTP_201_CREATED)

    def test_ok_creation_simple_complet(self):
        self._create_or_update(data.test_ok_simple_complet, expected_status_code=status.HTTP_201_CREATED)

    def test_ok_creation_avec_cultures(self):
        self._create_or_update(data.test_ok_avec_cultures, expected_status_code=status.HTTP_201_CREATED)

    def test_ok_creation_avec_cultures_complet(self):
        self._create_or_update(data.test_ok_avec_cultures_complet,
                               expected_status_code=status.HTTP_201_CREATED)

    def test_ok_creation_employe(self):
        responsable = test_fixtures.create_user()
        employe = self.init_current_user()
        test_fixtures.create_ferme(responsable=responsable, employes=[employe])
        test_data = deepcopy(data.test_ok_simple)
        test_data["request"]["user_id"] = employe.id
        self._create_or_update(test_data, expected_status_code=status.HTTP_201_CREATED)

    def test_ok_creation_responsable_pour_employe(self):
        responsable = self.init_current_user()
        employe = test_fixtures.create_user()
        test_fixtures.create_ferme(responsable=responsable, employes=[employe])
        test_data = deepcopy(data.test_ok_simple)
        test_data["request"]["user_id"] = employe.id
        self._create_or_update(test_data, expected_status_code=status.HTTP_201_CREATED)

    def test_nok_parcelle_not_in_ferme(self):
        responsable = self.init_current_user()
        other_responsable = test_fixtures.create_user()
        test_fixtures.create_ferme(responsable=responsable)
        other_ferme = test_fixtures.create_ferme(responsable=other_responsable)
        parcelle_ferme = test_fixtures.create_parcelle(other_ferme, "Ma parcelle de ma ferme")
        parcelle_other_ferme = test_fixtures.create_parcelle(other_ferme, "La parcelle de l'autre ferme")
        test_data = deepcopy(data.test_ok_simple)
        test_data["parcelles_to_create"] = []
        test_data["request"]["user_id"] = responsable.id
        test_data["request"]["parcelle_ids"] = [parcelle_other_ferme.id, parcelle_ferme.id]
        self._create_or_update(test_data, expected_status_code=status.HTTP_404_NOT_FOUND)
        test_data["request"]["parcelle_ids"] = [parcelle_ferme.id]
        test_data["request"]["cultures"] = [
            {
                "culture_id": 5,
                "parcelle_ids": [parcelle_other_ferme.id, parcelle_ferme.id],
                "quantite": 12,
                "nature": "Montagne",
                "unite_id": 16
            }
        ]
        self._create_or_update(test_data, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_creation_user_not_exists(self):
        test_data = deepcopy(data.test_ok_simple)
        self.init_current_user()
        test_fixtures.create_ferme(responsable=self.get_current_user())
        test_data["request"]["user_id"] = 999
        self._create_or_update(test_data, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_creation_user_not_in_ferme(self):
        responsable = self.init_current_user()
        user_not_in_ferme = test_fixtures.create_user()
        test_fixtures.create_ferme(responsable=responsable)
        test_data = deepcopy(data.test_ok_simple)
        test_data["request"]["user_id"] = user_not_in_ferme.id
        self._create_or_update(test_data, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_creation_activite_not_exists(self):
        test_data = deepcopy(data.test_ok_simple)
        test_data["request"]["activite_id"] = 999
        self._create_or_update(test_data, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_creation_culture_not_exists(self):
        test_data = deepcopy(data.test_ok_simple)
        test_data["request"]["cultures"] = [
            {
                "culture_id": 999,
                "parcelle_ids": [],
                "quantite": 12,
                "nature": "Montagne",
                "unite_id": 16
            }
        ]
        self._create_or_update(test_data, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_creation_parcelle_not_exists(self):
        test_data = deepcopy(data.test_ok_simple)
        test_data["request"]["cultures"] = [
            {
                "culture_id": 5,
                "parcelle_ids": [1, 99],
                "quantite": 12,
                "nature": "Montagne",
                "unite_id": 16
            }
        ]
        self._create_or_update(test_data, expected_status_code=status.HTTP_404_NOT_FOUND)
        test_data2 = deepcopy(data.test_ok_simple)
        test_data2["request"]["cultures"] = []
        test_data2["request"]["parcelle_ids"] = [999, 2]
        self._create_or_update(test_data2, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_creation_date_invalide(self):
        test_data = deepcopy(data.test_ok_simple)
        test_data["request"]["date"] = "35/12/2025"
        self._create_or_update(test_data, expected_status_code=status.HTTP_400_BAD_REQUEST)
        test_data["request"]["date"] = "12/13/2025"
        self._create_or_update(test_data, expected_status_code=status.HTTP_400_BAD_REQUEST)
        test_data["request"]["date"] = "11/08/857"
        self._create_or_update(test_data, expected_status_code=status.HTTP_400_BAD_REQUEST)

    def test_nok_creation_duree_invalide(self):
        test_data = deepcopy(data.test_ok_simple)
        test_data["request"]["duree_minutes"] = -9
        self._create_or_update(test_data, expected_status_code=status.HTTP_400_BAD_REQUEST)
        test_data["request"]["duree_minutes"] = 0
        self._create_or_update(test_data, expected_status_code=status.HTTP_400_BAD_REQUEST)
        test_data["request"]["duree_minutes"] = 987652327
        self._create_or_update(test_data, expected_status_code=status.HTTP_400_BAD_REQUEST)

    def test_nok_creation_employe_pour_responsable(self):
        responsable = test_fixtures.create_user()
        employe = self.init_current_user()
        test_fixtures.create_ferme(responsable=responsable, employes=[employe])
        test_data = deepcopy(data.test_ok_simple)
        test_data["request"]["user_id"] = responsable.id
        self._create_or_update(test_data, expected_status_code=status.HTTP_403_FORBIDDEN)

    def test_nok_creation_employe_pour_autre_employe(self):
        responsable = test_fixtures.create_user()
        employe = self.init_current_user()
        other_employe = test_fixtures.create_user()
        test_fixtures.create_ferme(responsable=responsable, employes=[employe, other_employe])
        test_data = deepcopy(data.test_ok_simple)
        test_data["request"]["user_id"] = other_employe.id
        self._create_or_update(test_data, expected_status_code=status.HTTP_403_FORBIDDEN)


class TestUpdateTache(TestTache):
    def _update(self, test_data, expected_status_code):
        test_data_copy = deepcopy(test_data)
        # Ajout de l'ID du user dans la requête qui diffère à chaque test
        if self.get_current_user() is None:
            self.init_current_user()
            test_fixtures.create_ferme(responsable=self.get_current_user())
        if test_data_copy["request"]["user_id"] is None:
            test_data_copy["request"]["user_id"] = self.get_current_user().id
        ferme = get_ferme_for_user(test_data_copy["request"]["user_id"])
        old_tache = test_fixtures.create_tache(user_id=test_data_copy["request"]["user_id"], ferme=ferme,
                                               nb_parcelles=4)
        old_parcelle_ids = [model_to_dict(parcelle).get("id") for parcelle in old_tache.parcelles.all()]
        old_culture_ids = [model_to_dict(culture).get("id") for culture in old_tache.cultures.all()]
        self._create_or_update(test_data_copy, expected_status_code=expected_status_code, tache_id=old_tache.id)
        new_tache = Tache.objects.get(id=old_tache.id)

        if expected_status_code == status.HTTP_200_OK:
            # On vérifie les modifications sur les parcelles
            for old_parcelle_id in old_parcelle_ids:
                self.assertIsNotNone(Parcelle.objects.get(
                    id=old_parcelle_id))  # on vérifie que la parcelle n'a pas été supprimée de la DB
                self.assertFalse(old_parcelle_id in map(lambda new_parcelle: new_parcelle.id,
                                                        new_tache.parcelles.all()))  # on vérifie que les anciennes parcelles ne sont plus reliées à la tâche

                # On vérifie que les anciennes culture_tâches ont été supprimées
                for old_culture_tache_id in old_culture_ids:
                    self.assertRaises(CultureTache.DoesNotExist, CultureTache.objects.get, id=old_culture_tache_id)
                    self.assertFalse(old_culture_tache_id in map(lambda new_culture_tache: new_culture_tache.id,
                                                                 new_tache.cultures.all()))

    def test_ok_update_simple(self):
        self._update(data.test_ok_simple, expected_status_code=status.HTTP_200_OK)

    def test_ok_update_simple_complet(self):
        self._update(data.test_ok_simple_complet, expected_status_code=status.HTTP_200_OK)

    def test_ok_update_avec_cultures(self):
        self._update(data.test_ok_avec_cultures, expected_status_code=status.HTTP_200_OK)

    def test_ok_update_avec_cultures_complet(self):
        self._update(data.test_ok_avec_cultures_complet,
                     expected_status_code=status.HTTP_200_OK)

    def test_ok_update_employe(self):
        responsable = test_fixtures.create_user()
        employe = self.init_current_user()
        test_fixtures.create_ferme(responsable=responsable, employes=[employe])
        test_data = deepcopy(data.test_ok_simple)
        test_data["request"]["user_id"] = employe.id
        self._update(test_data, expected_status_code=status.HTTP_200_OK)

    def test_ok_update_responsable_pour_employe(self):
        responsable = self.init_current_user()
        employe = test_fixtures.create_user()
        test_fixtures.create_ferme(responsable=responsable, employes=[employe])
        test_data = deepcopy(data.test_ok_simple)
        test_data["request"]["user_id"] = employe.id
        self._update(test_data, expected_status_code=status.HTTP_200_OK)

    def test_nok_parcelle_not_in_ferme(self):
        responsable = self.init_current_user()
        other_responsable = test_fixtures.create_user()
        test_fixtures.create_ferme(responsable=responsable)
        other_ferme = test_fixtures.create_ferme(responsable=other_responsable)
        parcelle_ferme = test_fixtures.create_parcelle(other_ferme, "Ma parcelle de ma ferme")
        parcelle_other_ferme = test_fixtures.create_parcelle(other_ferme, "La parcelle de l'autre ferme")
        test_data = deepcopy(data.test_ok_simple)
        test_data["parcelles_to_create"] = []
        test_data["request"]["user_id"] = responsable.id
        test_data["request"]["parcelle_ids"] = [parcelle_other_ferme.id, parcelle_ferme.id]
        self._update(test_data, expected_status_code=status.HTTP_404_NOT_FOUND)
        test_data["parcelles_to_create"] = []
        test_data["request"]["parcelle_ids"] = [parcelle_ferme.id]
        test_data["request"]["user_id"] = responsable.id
        test_data["request"]["cultures"] = [
            {
                "culture_id": 5,
                "parcelle_ids": [parcelle_other_ferme.id, parcelle_ferme.id],
                "quantite": 12,
                "nature": "Montagne",
                "unite_id": 16
            }
        ]
        self._update(test_data, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_update_activite_not_exists(self):
        test_data = deepcopy(data.test_ok_simple)
        test_data["request"]["activite_id"] = 999
        self._update(test_data, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_update_culture_not_exists(self):
        test_data = deepcopy(data.test_ok_simple)
        test_data["request"]["cultures"] = [
            {
                "culture_id": 999,
                "parcelle_ids": [],
                "quantite": 12,
                "nature": "Montagne",
                "unite_id": 16
            }
        ]
        self._update(test_data, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_update_parcelle_not_exists(self):
        test_data = deepcopy(data.test_ok_simple)
        test_data["request"]["cultures"] = [
            {
                "culture_id": 5,
                "parcelle_ids": [1, 99],
                "quantite": 12,
                "nature": "Montagne",
                "unite_id": 16
            }
        ]
        self._update(test_data, expected_status_code=status.HTTP_404_NOT_FOUND)
        test_data2 = deepcopy(data.test_ok_simple)
        test_data2["request"]["cultures"] = []
        test_data2["request"]["parcelle_ids"] = [999, 2]
        self._update(test_data2, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_update_date_invalide(self):
        test_data = deepcopy(data.test_ok_simple)
        test_data["request"]["date"] = "35/12/2025"
        self._update(test_data, expected_status_code=status.HTTP_400_BAD_REQUEST)
        test_data["request"]["date"] = "12/13/2025"
        self._update(test_data, expected_status_code=status.HTTP_400_BAD_REQUEST)
        test_data["request"]["date"] = "11/08/857"
        self._update(test_data, expected_status_code=status.HTTP_400_BAD_REQUEST)

    def test_nok_update_duree_invalide(self):
        test_data = deepcopy(data.test_ok_simple)
        test_data["request"]["duree_minutes"] = -9
        self._update(test_data, expected_status_code=status.HTTP_400_BAD_REQUEST)
        test_data["request"]["duree_minutes"] = 0
        self._update(test_data, expected_status_code=status.HTTP_400_BAD_REQUEST)
        test_data["request"]["duree_minutes"] = 987652327
        self._update(test_data, expected_status_code=status.HTTP_400_BAD_REQUEST)

    def test_nok_update_employe_pour_responsable(self):
        responsable = test_fixtures.create_user()
        employe = self.init_current_user()
        test_fixtures.create_ferme(responsable=responsable, employes=[employe])
        test_data = deepcopy(data.test_ok_simple)
        test_data["request"]["user_id"] = responsable.id
        self._update(test_data, expected_status_code=status.HTTP_403_FORBIDDEN)

    def test_nok_update_employe_pour_autre_employe(self):
        responsable = test_fixtures.create_user()
        employe = self.init_current_user()
        other_employe = test_fixtures.create_user()
        test_fixtures.create_ferme(responsable=responsable, employes=[employe, other_employe])
        test_data = deepcopy(data.test_ok_simple)
        test_data["request"]["user_id"] = other_employe.id
        self._update(test_data, expected_status_code=status.HTTP_403_FORBIDDEN)


class TestGetTache(SebaniaTestCase):
    url = reverse_lazy('taches-list')

    def _create_data(self, user: User, ferme: Ferme, date: datetime.datetime = timezone.now()):
        other_date = timezone.now() - datetime.timedelta(days=1)
        other_ferme = test_fixtures.create_ferme()
        other_user = test_fixtures.create_user()
        # création de tâches qui correspondent aux filtres
        matching_taches = []
        for _ in range(6):
            matching_taches.append(test_fixtures.create_tache(ferme=ferme, user_id=user.id, nb_parcelles=3, date=date))
        # création de tâches qui ne correspondant pas aux filtres
        for _ in range(5):
            test_fixtures.create_tache(ferme=other_ferme, user_id=user.id, nb_parcelles=3, date=date)
            test_fixtures.create_tache(ferme=ferme, user_id=other_user.id, nb_parcelles=3, date=date)
            test_fixtures.create_tache(ferme=ferme, user_id=user.id, nb_parcelles=3, date=other_date)
        return matching_taches

    def _compare_response_with_expected(self, response, expected_taches: List[Tache]):
        if len(expected_taches) == 1:
            actual_taches = [json.loads(response.content)]
        else:
            actual_taches = json.loads(response.content)
        self.assertEqual(len(actual_taches), len(expected_taches))
        for actual_tache in actual_taches:
            expected_tache = next((x for x in expected_taches if x.id == actual_tache.get("id")), None)
            self.assertIsNotNone(expected_tache)
            self.assertEqual(expected_tache.parcelles.count(), len(actual_tache.get("parcelles")))
            self.assertEqual(expected_tache.cultures.count(), len(actual_tache.get("cultures")))
            expected_response = {
                "id": expected_tache.id,
                "date": expected_tache.date.strftime("%d/%m/%Y"),
                "activite": {
                    "id": expected_tache.activite.id,
                    "nom": expected_tache.activite.nom,
                    "niveau_complexite": expected_tache.activite.niveau_complexite,
                    "unites": "no_check"
                },
                "user": {
                    "id": expected_tache.user.id,
                    "email": "no_check",
                    "first_name": "no_check",
                    "last_name": "no_check",
                    "roles": "no_check",
                },
                "duree_minutes": expected_tache.duree_minutes,
                "cultures": "no_check",
                "commentaire": expected_tache.commentaire,
                "parcelles": "no_check",
                "quantite": expected_tache.quantite,
                "unite": {
                    "id": expected_tache.unite_id,
                    "nom": expected_tache.unite.nom
                },
                "nature": expected_tache.nature,
                "fields_are_missing": "no_check",
                "vocal_id": "no_check"
            }
            self.check_response(expected_response, actual_tache)
            self._compare_parcelles(expected_tache.parcelles.all(), actual_tache.get("parcelles"))
            self._compare_cultures(expected_tache.cultures.all(), actual_tache.get("cultures"), expected_tache.activite.niveau_complexite)

    def _compare_parcelles(self, expected_parcelles,  actual_parcelles):
        for expected_parcelle in expected_parcelles:
            actual_parcelle = next(
                (x for x in actual_parcelles if x.get("id") == expected_parcelle.id), None)
            self.assertIsNotNone(actual_parcelle)
            expected_response_parcelle = {
                "id": expected_parcelle.id,
                "nom": expected_parcelle.nom,
            }
            self.check_response(expected_response_parcelle, actual_parcelle)

    def _compare_cultures(self, expected_cultures,  actual_cultures, niveau_complexite: int):
        for expected_culture in expected_cultures:
            actual_culture = next(
                (x for x in actual_cultures if x.get("culture").get("id") == expected_culture.culture.id), None)
            self.assertIsNotNone(actual_culture)
            expected_response_culture = {
                "culture": {
                    "id": expected_culture.culture.id,
                    "nom": expected_culture.culture.nom
                },
                "parcelles": "no_check",
                "quantite": expected_culture.quantite,
                "unite": {
                    "id": expected_culture.unite.id,
                    "nom": expected_culture.unite.nom,
                },
                "nature": expected_culture.nature,
                "fields_are_missing": expected_culture.get_fields_are_missing(niveau_complexite),
            }
            self.check_response(expected_response_culture, actual_culture)
            self._compare_parcelles(expected_culture.parcelles.all(), actual_culture.get("parcelles"))

    def test_ok_get_one(self):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        existing_tache = test_fixtures.create_tache(ferme=ferme, user_id=responsable.id, nb_parcelles=3)
        response = self.client.get(_get_url_detail(existing_tache.id), headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._compare_response_with_expected(response, [existing_tache])

    def test_ok_get_all(self):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        existing_taches = []
        for _ in range(6):
            existing_taches.append(test_fixtures.create_tache(ferme=ferme, user_id=responsable.id, nb_parcelles=3))
        response = self.client.get(self.url, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._compare_response_with_expected(response, existing_taches)

    def test_ok_get_all_filters_date_user(self):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        date = timezone.now()
        matching_taches = self._create_data(date=date, user=responsable, ferme=ferme)
        data = {
            "user_id": responsable.id,
            "date": date.strftime("%d/%m/%Y"),
        }
        response = self.client.get(self.url, data=data, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._compare_response_with_expected(response, matching_taches)


class TestDeleteTache(SebaniaTestCase):
    def _delete(self, tache_id: int = None, user_tache: User = None, user_delete: User = None, ferme: Ferme = None,
                expected_status_code: int = status.HTTP_204_NO_CONTENT):
        if user_delete is None:
            user_delete = self.init_current_user()
        if user_tache is None:
            user_tache = user_delete
        if ferme is None:
            ferme = test_fixtures.create_ferme(responsable=user_delete)
        # Création de la tâche en base
        if tache_id is None:
            tache = test_fixtures.create_tache(ferme=ferme, user_id=user_tache.id, nb_parcelles=3)
            tache_id = tache.id
        # Suppression
        response = self.client.delete(_get_url_detail(tache_id), headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, expected_status_code)
        # Vérification que la tâche n'est plus en base
        if expected_status_code == status.HTTP_204_NO_CONTENT:
            self.assertRaises(Tache.DoesNotExist, lambda: Tache.objects.get(id=tache_id))

    def test_ok_delete(self):
        self._delete()

    def test_ok_delete_responsable_pour_employe(self):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        employe = ferme.employes.first()
        self._delete(user_tache=employe, user_delete=responsable, ferme=ferme)

    def test_ok_delete_employe_pour_employe(self):
        employe1 = self.init_current_user()
        ferme = test_fixtures.create_ferme(employes=[employe1])
        self._delete(user_tache=employe1, user_delete=employe1, ferme=ferme)

    def test_nok_delete_id_not_exists(self):
        self._delete(tache_id=99, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_delete_employe_pour_responsable(self):
        employe1 = self.init_current_user()
        responsable = test_fixtures.create_user()
        ferme = test_fixtures.create_ferme(employes=[employe1], responsable=responsable)
        self._delete(user_tache=responsable, user_delete=employe1, ferme=ferme,
                     expected_status_code=status.HTTP_403_FORBIDDEN)

    def test_nok_delete_employe_pour_autre_employe(self):
        employe1 = self.init_current_user()
        employe2 = test_fixtures.create_user()
        ferme = test_fixtures.create_ferme(employes=[employe1, employe2])
        self._delete(user_tache=employe2, user_delete=employe1, ferme=ferme,
                     expected_status_code=status.HTTP_403_FORBIDDEN)

    def test_nok_delete_responsable_pour_autre_ferme(self):
        responsable = self.init_current_user()
        autre_responsable = test_fixtures.create_user()
        test_fixtures.create_ferme(responsable=responsable)
        autre_ferme = test_fixtures.create_ferme(responsable=autre_responsable)
        self._delete(user_tache=autre_responsable, user_delete=responsable, ferme=autre_ferme,
                     expected_status_code=status.HTTP_404_NOT_FOUND)
