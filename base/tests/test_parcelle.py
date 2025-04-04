import json

from rest_framework import status
from rest_framework.reverse import reverse_lazy

from base.models import Parcelle, TypeParcelle, Ferme, User
from sebania.tests import test_fixtures
from sebania.tests.SebaniaTestCase import SebaniaTestCase
from sebania.utils import crypto_utils


def _get_url_detail(parcelle_id: int):
    return reverse_lazy('parcelles-detail', args=[parcelle_id])


class TestParcelle(SebaniaTestCase):
    url_list = reverse_lazy('parcelles-list')

    def _check_response(self, request, response, ferme: Ferme):
        response_data = json.loads(response.content)
        self.assertIsNotNone(response_data.get("id"))
        self.assertEqual(response_data.get("nom"), request.get("nom"))
        self.assertEqual(response_data.get("superficie"), request.get("superficie"))
        self.assertEqual(response_data.get("type").get("id"), request.get("type_id"))
        self.assertIsNotNone(response_data.get("type").get("nom"))
        parcelle_id = response_data.get("id")
        self._check_in_database(request, parcelle_id, ferme)

    def _compare_instance_and_response(self, response):
        response_data = json.loads(response.content)
        instance = Parcelle.objects.get(id=response_data.get("id"))
        self.assertEqual(response_data.get("id"), instance.id)
        self.assertEqual(response_data.get("nom"), instance.nom)
        self.assertEqual(response_data.get("superficie"), instance.superficie)
        self.assertEqual(response_data.get("type").get("id"), instance.type.id)
        self.assertEqual(response_data.get("type").get("nom"), instance.type.nom)

    def _check_in_database(self, request, parcelle_id, ferme: Ferme):
        parcelle = Parcelle.objects.get(id=parcelle_id)
        type_parcelle = TypeParcelle.objects.get(id=request.get("type_id"))
        self.assertEqual(parcelle.nom, request.get("nom"))
        self.assertEqual(parcelle.type, type_parcelle)
        self.assertEqual(parcelle.superficie, request.get("superficie"))
        self.assertEqual(parcelle.ferme, ferme)

    def _send_parcelle_and_check_response(self, parcelle_id: int  = None, nom: str = crypto_utils.random_string(), superficie: float = 120.0, type_id: int = 1,
                         user: User = None, ferme: Ferme = None,
                         expected_status_code: int = status.HTTP_200_OK):
        if user is None:
            user = self.init_current_user()
        if ferme is None:
            ferme = test_fixtures.create_ferme(responsable=user)
        request = {
            "nom": nom,
            "superficie": superficie,
            "type_id": type_id,
        }
        # UPDATE
        if parcelle_id is not None:
            response = self.client.put(_get_url_detail(parcelle_id), request, headers=self.get_jwt_headers(), format='json')
        # CREATE
        else:
            response = self.client.post(self.url_list, request, headers=self.get_jwt_headers(), format='json')
        self.assertEqual(response.status_code, expected_status_code)
        if expected_status_code == status.HTTP_200_OK or expected_status_code == status.HTTP_201_CREATED:
            self._check_response(request, response, ferme)

    def _update_parcelle(self, parcelle_id: int  = None, nom: str = crypto_utils.random_string(), superficie: float = 120.0, type_id: int = 1,
                         user: User = None, ferme: Ferme = None,
                         expected_status_code: int = status.HTTP_200_OK):
        if user is None:
            user = self.init_current_user()
        if ferme is None:
            ferme = test_fixtures.create_ferme(responsable=user)
        if parcelle_id is None:
            existing_parcelle = test_fixtures.create_parcelle(ferme)
            parcelle_id = existing_parcelle.id
        self._send_parcelle_and_check_response(expected_status_code=expected_status_code, parcelle_id=parcelle_id, ferme=ferme, user=user,
                                               nom=nom, superficie=superficie, type_id=type_id)

    def _delete_parcelle(self, parcelle_id: int = None, user: User = None, ferme: Ferme = None, expected_status_code: int = status.HTTP_200_OK):
        if user is None:
            user = self.init_current_user()
        if ferme is None:
            ferme = test_fixtures.create_ferme(responsable=user)
        # Create existing parcelle
        if parcelle_id is None:
            parcelle = test_fixtures.create_parcelle(ferme)
            parcelle_id = parcelle.id
        response = self.client.delete(_get_url_detail(parcelle_id), headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, expected_status_code)
        if expected_status_code == status.HTTP_204_NO_CONTENT:
            self.assertRaises(Parcelle.DoesNotExist, Parcelle.objects.get, id=parcelle_id)

    def _get_one_parcelle(self, parcelle_id: int = None, expected_status_code: int = status.HTTP_200_OK):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        if parcelle_id is None:
            parcelle = test_fixtures.create_parcelle(ferme)
            parcelle_id = parcelle.id
        response = self.client.get(_get_url_detail(parcelle_id), headers=self.get_jwt_headers())
        self.assertEqual(expected_status_code, response.status_code)
        if expected_status_code == status.HTTP_200_OK:
            self._compare_instance_and_response(response)

    def _create_parcelles(self, nb_parcelles):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        parcelles = []
        for _ in range(nb_parcelles):
            parcelles.append(test_fixtures.create_parcelle(ferme))
        return parcelles

    def _check_nb_parcelles_in_response(self, response, nb_parcelles):
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data), nb_parcelles)

    def test_ok_create(self):
        self._send_parcelle_and_check_response(expected_status_code=status.HTTP_201_CREATED)

    def test_ok_create_nom_already_exists_different_ferme(self):
        other_ferme = test_fixtures.create_ferme()
        existing_parcelle = test_fixtures.create_parcelle(other_ferme)
        self._send_parcelle_and_check_response(expected_status_code=status.HTTP_201_CREATED, nom=existing_parcelle.nom)

    def test_nok_create_type_not_exists(self):
        self._send_parcelle_and_check_response(expected_status_code=status.HTTP_404_NOT_FOUND, type_id=99)

    def test_nok_create_nom_already_exists(self):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        existing_parcelle = test_fixtures.create_parcelle(ferme)
        self._send_parcelle_and_check_response(expected_status_code=status.HTTP_400_BAD_REQUEST, nom=existing_parcelle.nom, ferme=ferme, user=responsable)

    def test_nok_create_superficie_zero(self):
        self._send_parcelle_and_check_response(expected_status_code=status.HTTP_400_BAD_REQUEST, superficie=0)

    def test_ok_update(self):
        self._update_parcelle(expected_status_code=status.HTTP_200_OK)

    def test_ok_update_nom_already_exists_different_ferme(self):
        other_ferme = test_fixtures.create_ferme()
        existing_parcelle = test_fixtures.create_parcelle(other_ferme)
        self._update_parcelle(expected_status_code=status.HTTP_200_OK, nom=existing_parcelle.nom)

    def test_nok_update_id_not_exists(self):
        self._update_parcelle(expected_status_code=status.HTTP_404_NOT_FOUND, parcelle_id=235)

    def test_nok_update_type_not_exists(self):
        self._update_parcelle(expected_status_code=status.HTTP_404_NOT_FOUND, type_id=99)

    def test_nok_update_nom_already_exists(self):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        existing_parcelle = test_fixtures.create_parcelle(ferme)
        self._update_parcelle(expected_status_code=status.HTTP_400_BAD_REQUEST, nom=existing_parcelle.nom, ferme=ferme, user=responsable)

    def test_nok_update_superficie_zero(self):
        self._update_parcelle(expected_status_code=status.HTTP_400_BAD_REQUEST, superficie=0)

    def test_ok_delete(self):
        self._delete_parcelle(expected_status_code=status.HTTP_204_NO_CONTENT)

    def test_nok_delete_id_not_exists(self):
        self._delete_parcelle(expected_status_code=status.HTTP_404_NOT_FOUND, parcelle_id=465)

    def test_nok_delete_employe_not_allowed(self):
        responsable = test_fixtures.create_user()
        employe = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable, employes=[employe])
        self._delete_parcelle(expected_status_code=status.HTTP_403_FORBIDDEN, user=employe, ferme=ferme)

    def test_ok_get_one(self):
        self._get_one_parcelle(expected_status_code=status.HTTP_200_OK)

    def test_nok_get_one_id_not_exists(self):
        self._get_one_parcelle(expected_status_code=status.HTTP_404_NOT_FOUND, parcelle_id=896)

    def test_ok_get_all(self):
        parcelles = self._create_parcelles(5)
        response = self.client.get(self.url_list, headers=self.get_jwt_headers())
        self._check_nb_parcelles_in_response(response, len(parcelles))

    def test_ok_get_all_create_delete(self):
        # Create 5 parcelles
        parcelles = self._create_parcelles(5)
        response = self.client.get(self.url_list, headers=self.get_jwt_headers())
        self._check_nb_parcelles_in_response(response, len(parcelles))

        # Delete 2 parcelles
        Parcelle.objects.get(id=parcelles[0].id).delete()
        Parcelle.objects.get(id=parcelles[2].id).delete()

        # Should get 3 parcelles
        response = self.client.get(self.url_list, headers=self.get_jwt_headers())
        self._check_nb_parcelles_in_response(response, len(parcelles) - 2)