import json

from rest_framework import status
from rest_framework.reverse import reverse_lazy

from base.models import Parcelle, Ferme, User
from sebania.tests import test_fixtures
from sebania.tests.SebaniaTestCase import SebaniaTestCase
from sebania.utils.db_utils import get_one_or_none, get_ferme_for_user


def _get_url_detail(parcelle_id: int):
    return reverse_lazy('parcelles-detail', args=[parcelle_id])


class TestParcelle(SebaniaTestCase):
    url_list = reverse_lazy('parcelles-list')

    def _send_request_and_check_response(self, request, expected_response, expected_entity, parcelle_id: int = None, expected_status_code: int = status.HTTP_200_OK):
        if self.get_current_user() is None:
            test_fixtures.create_ferme(responsable=self.init_current_user())
        # UPDATE
        if parcelle_id is not None:
            response = self.client.put(_get_url_detail(parcelle_id), request, headers=self.get_jwt_headers(),
                                       format='json')
        # CREATE
        else:
            response = self.client.post(self.url_list, request, headers=self.get_jwt_headers(), format='json')
        self.assertEqual(response.status_code, expected_status_code)
        if expected_status_code <= status.HTTP_201_CREATED:
            response_data = json.loads(response.content)
            self.check_response(expected_response, response_data)
            parcelle = Parcelle.objects.get(id=response_data.get("id"), ferme=get_ferme_for_user(self.get_current_user().id))
            self.check_entity(expected_entity, parcelle)

    def _update_parcelle(self, request, expected_response, expected_entity, parcelle_id: int = None,
                         expected_status_code: int = status.HTTP_200_OK):
        if self.get_current_user() is None:
            user = self.init_current_user()
            ferme = test_fixtures.create_ferme(responsable=user)
            if parcelle_id is None:
                existing_parcelle = test_fixtures.create_parcelle(ferme)
                parcelle_id = existing_parcelle.id
        self._send_request_and_check_response(expected_status_code=expected_status_code, parcelle_id=parcelle_id,
                                               request=request, expected_response=expected_response, expected_entity=expected_entity)

    def _delete_parcelle(self, parcelle_id: int = None, user: User = None, ferme: Ferme = None,
                         expected_status_code: int = status.HTTP_200_OK):
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
        else:
            parcelle = get_one_or_none(Parcelle, id=parcelle_id)
        if parcelle is not None:
            expected_response = {
                "id": parcelle_id,
                "nom": parcelle.nom,
                "longueur": parcelle.longueur,
                "largeur": parcelle.largeur,
                "largeur_planche": parcelle.largeur_planche,
                "nombre_planches": parcelle.nombre_planches,
                "largeur_passe_pieds": parcelle.largeur_passe_pieds,
                "superficie": parcelle.superficie,
                "superficie_cultivee": parcelle.superficie_cultivee,
                "type": "is_none"
            }
            if parcelle.type_id is not None:
                expected_response["type"] = {
                    "id": parcelle.type_id,
                    "nom": parcelle.type.nom
                }
        response = self.client.get(_get_url_detail(parcelle_id), headers=self.get_jwt_headers())
        self.assertEqual(expected_status_code, response.status_code)
        if expected_status_code == status.HTTP_200_OK:
            response_data = json.loads(response.content)
            self.check_response(expected_response, response_data)

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

    def test_ok_create_complet(self):
        request = {
            "nom": "Ma parcelle",
            "longueur": 120,
            "largeur": 30,
            "largeur_planche": 0.8,
            "nombre_planches": 30,
            "type_id": 1,
        }
        expected_response = {
            "id": "no_check",
            "nom": "Ma parcelle",
            "longueur": 120,
            "largeur": 30,
            "largeur_planche": 0.8,
            "largeur_passe_pieds": 0.2,
            "superficie": 3600,
            "superficie_cultivee": 2880,
            "nombre_planches": 30,
            "type": {
                "id": 1,
                "nom": "Plein champ",
            }
        }
        expected_entity = {
            "nom": "Ma parcelle",
            "longueur": 120,
            "largeur": 30,
            "largeur_planche": 0.8,
            "largeur_passe_pieds": 0.2,
            "superficie": 3600,
            "superficie_cultivee": 2880,
            "nombre_planches": 30,
            "type_id": 1,
        }
        self._send_request_and_check_response(request, expected_response, expected_entity, expected_status_code=status.HTTP_201_CREATED)

    def test_ok_create_nom_already_exists_different_ferme(self):
        other_ferme = test_fixtures.create_ferme()
        existing_parcelle = test_fixtures.create_parcelle(other_ferme)
        request = {
            "nom": existing_parcelle.nom,
            "longueur": 120,
            "largeur": 30,
            "largeur_planche": 0.8,
            "nombre_planches": 30,
            "type_id": 1,
        }
        expected_response = {
            "id": "no_check",
            "nom": existing_parcelle.nom,
            "longueur": 120,
            "largeur": 30,
            "largeur_planche": 0.8,
            "largeur_passe_pieds": 0.2,
            "superficie": 3600,
            "superficie_cultivee": 2880,
            "nombre_planches": 30,
            "type": {
                "id": 1,
                "nom": "Plein champ",
            }
        }
        expected_entity = {
            "nom": existing_parcelle.nom,
        }
        self._send_request_and_check_response(request, expected_response, expected_entity, expected_status_code=status.HTTP_201_CREATED)

    def test_nok_create_type_not_exists(self):
        request = {
            "nom": "Ma parcelle",
            "longueur": 120,
            "largeur": 30,
            "largeur_planche": 0.8,
            "nombre_planches": 30,
            "type_id": 99,
        }
        self._send_request_and_check_response(request, None, None, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_create_nom_already_exists(self):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        existing_parcelle = test_fixtures.create_parcelle(ferme)
        request = {
            "nom": existing_parcelle.nom,
            "type_id": 1,
        }
        self._send_request_and_check_response(request, None, None, expected_status_code=status.HTTP_400_BAD_REQUEST)

    def test_nok_create_longueur_zero(self):
        request = {
            "nom": "Ma parcelle",
            "longueur": 0,
            "largeur": 30,
            "largeur_planche": 0.8,
            "nombre_planches": 30,
            "type_id": 1,
        }
        self._send_request_and_check_response(request, None, None, expected_status_code=status.HTTP_400_BAD_REQUEST)

    def test_nok_create_largeur_zero(self):
        request = {
            "nom": "Ma parcelle",
            "longueur": 120,
            "largeur": 0,
            "largeur_planche": 0.8,
            "nombre_planches": 30,
            "type_id": 1,
        }
        self._send_request_and_check_response(request, None, None, expected_status_code=status.HTTP_400_BAD_REQUEST)

    def test_ok_update(self):
        request = {
            "nom": "Ma parcelle",
            "longueur": 120,
            "largeur": 30,
            "largeur_planche": 0.8,
            "nombre_planches": 30,
            "type_id": 1,
        }
        expected_response = {
            "id": "no_check",
            "nom": "Ma parcelle",
            "longueur": 120,
            "largeur": 30,
            "largeur_planche": 0.8,
            "largeur_passe_pieds": 0.2,
            "superficie": 3600,
            "superficie_cultivee": 2880,
            "nombre_planches": 30,
            "type": {
                "id": 1,
                "nom": "Plein champ",
            }
        }
        expected_entity = {
            "nom": "Ma parcelle",
            "longueur": 120,
            "largeur": 30,
            "largeur_planche": 0.8,
            "largeur_passe_pieds": 0.2,
            "superficie": 3600,
            "superficie_cultivee": 2880,
            "nombre_planches": 30,
            "type_id": 1,
        }
        self._update_parcelle(request, expected_response, expected_entity, expected_status_code=status.HTTP_200_OK)

    def test_ok_update_nom_inchange(self):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        existing_parcelle = test_fixtures.create_parcelle(ferme)
        request = {
            "nom": existing_parcelle.nom,
            "longueur": 120,
            "largeur": 30,
            "largeur_planche": 0.8,
            "nombre_planches": 30,
            "type_id": 1,
        }
        expected_response = {
            "id": "no_check",
            "nom": existing_parcelle.nom,
            "longueur": 120,
            "largeur": 30,
            "largeur_planche": 0.8,
            "largeur_passe_pieds": 0.2,
            "superficie": 3600,
            "superficie_cultivee": 2880,
            "nombre_planches": 30,
            "type": {
                "id": 1,
                "nom": "Plein champ",
            }
        }
        expected_entity = {
            "nom": existing_parcelle.nom,
            "longueur": 120,
            "largeur": 30,
            "largeur_planche": 0.8,
            "largeur_passe_pieds": 0.2,
            "superficie": 3600,
            "superficie_cultivee": 2880,
            "nombre_planches": 30,
            "type_id": 1,
        }
        self._update_parcelle(request, expected_response, expected_entity, expected_status_code=status.HTTP_200_OK, parcelle_id=existing_parcelle.id)

    def test_ok_update_nom_already_exists_different_ferme(self):
        user = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=user)
        other_ferme = test_fixtures.create_ferme()
        existing_parcelle_on_other_ferme = test_fixtures.create_parcelle(other_ferme)
        parcelle_to_update = test_fixtures.create_parcelle(ferme)
        request = {
            "nom": existing_parcelle_on_other_ferme.nom,
            "longueur": 120,
            "largeur": 30,
            "largeur_planche": 0.8,
            "nombre_planches": 30,
            "type_id": 3,
        }
        expected_response = {
            "id": "no_check",
            "nom": existing_parcelle_on_other_ferme.nom,
            "longueur": 120,
            "largeur": 30,
            "largeur_planche": 0.8,
            "largeur_passe_pieds": 0.2,
            "superficie": 3600,
            "superficie_cultivee": 2880,
            "nombre_planches": 30,
            "type": {
                "id": 3,
                "nom": "no_check",
            }
        }
        expected_entity = {
            "nom": existing_parcelle_on_other_ferme.nom,
            "longueur": 120,
            "largeur": 30,
            "largeur_planche": 0.8,
            "largeur_passe_pieds": 0.2,
            "superficie": 3600,
            "superficie_cultivee": 2880,
            "nombre_planches": 30,
            "type_id": 3,
        }
        self._update_parcelle(request, expected_response, expected_entity, expected_status_code=status.HTTP_200_OK, parcelle_id=parcelle_to_update.id)

    def test_nok_update_id_not_exists(self):
        request = {
            "nom": "Ma parcelle",
            "longueur": 120,
            "largeur": 30,
            "largeur_planche": 0.8,
            "nombre_planches": 30,
            "type_id": 1,
        }
        self._update_parcelle(request, None, None, expected_status_code=status.HTTP_404_NOT_FOUND, parcelle_id=235)

    def test_nok_update_type_not_exists(self):
        request = {
            "nom": "Ma parcelle",
            "longueur": 120,
            "largeur": 30,
            "largeur_planche": 0.8,
            "nombre_planches": 30,
            "type_id": 99,
        }
        self._update_parcelle(request, None, None, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_update_nom_already_exists(self):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        existing_parcelle = test_fixtures.create_parcelle(ferme)
        request = {
            "nom": existing_parcelle.nom,
            "longueur": 120,
            "largeur": 30,
            "largeur_planche": 0.8,
            "nombre_planches": 30,
            "type_id": 1,
        }
        self._update_parcelle(request, None, None, expected_status_code=status.HTTP_400_BAD_REQUEST)

    def test_nok_update_longueur_zero(self):
        request = {
            "nom": "Ma parcelle",
            "longueur": 0,
            "largeur": 30,
            "largeur_planche": 0.8,
            "nombre_planches": 30,
            "type_id": 1,
        }
        self._update_parcelle(request, None, None, expected_status_code=status.HTTP_400_BAD_REQUEST)

    def test_nok_update_largeur_zero(self):
        request = {
            "nom": "Ma parcelle",
            "longueur": 120,
            "largeur": 0,
            "largeur_planche": 0.8,
            "nombre_planches": 30,
            "type_id": 1,
        }
        self._update_parcelle(request, None, None, expected_status_code=status.HTTP_400_BAD_REQUEST)

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
