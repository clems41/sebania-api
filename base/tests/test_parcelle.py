import json

from rest_framework import status
from rest_framework.reverse import reverse_lazy

from base.models import Parcelle, TypeParcelle, Ferme, User
from sebania.tests import test_fixtures
from sebania.tests.SebaniaTestCase import SebaniaTestCase
from sebania.utils import crypto_utils
from sebania.utils.db_utils import get_one_or_none


def _get_url_detail(parcelle_id: int):
    return reverse_lazy('parcelles-detail', args=[parcelle_id])


class TestParcelle(SebaniaTestCase):
    url_list = reverse_lazy('parcelles-list')

    def _send_parcelle_and_check_response(self, parcelle_id: int  = None, nom: str = crypto_utils.random_string(), longueur: float = 120.0,
                                          largeur: float = 120.0, largeur_planche: float | None = 0.8, nb_planches: int | None = 8, type_id: int | None = 1,
                         user: User = None, ferme: Ferme = None,
                         expected_status_code: int = status.HTTP_200_OK):
        if user is None:
            user = self.init_current_user()
        if ferme is None:
            ferme = test_fixtures.create_ferme(responsable=user)
        request = {
            "nom": nom,
            "longueur": longueur,
            "largeur": largeur,
            "largeur_planche": largeur_planche,
            "nombre_planches": nb_planches,
            "type_id": type_id,
        }
        expected_response = {
            "id": "no_check",
            "nom": nom,
            "longueur": longueur,
            "largeur": largeur,
            "largeur_planche": largeur_planche,
            "nombre_planches": nb_planches,
            "type": "is_none"
        }
        expected_entity = {
            "nom": nom,
            "longueur": longueur,
            "largeur": largeur,
            "largeur_planche": largeur_planche,
            "nombre_planches": nb_planches,
            "type_id": type_id,
            "ferme_id": ferme.id,
        }
        if type_id is not None:
            type_parcelle = get_one_or_none(TypeParcelle, id=type_id)
            if type_parcelle is not None:
                expected_response["type"] = {
                    "id": type_id,
                    "nom": type_parcelle.nom
                }
        # UPDATE
        if parcelle_id is not None:
            response = self.client.put(_get_url_detail(parcelle_id), request, headers=self.get_jwt_headers(), format='json')
        # CREATE
        else:
            response = self.client.post(self.url_list, request, headers=self.get_jwt_headers(), format='json')
        self.assertEqual(response.status_code, expected_status_code)
        if expected_status_code == status.HTTP_200_OK or expected_status_code == status.HTTP_201_CREATED:
            response_data = json.loads(response.content)
            self.check_response(expected_response, response_data)
            parcelle = Parcelle.objects.get(id=response_data.get("id"))
            self.check_entity(expected_entity, parcelle)

    def _update_parcelle(self, parcelle_id: int  = None, nom: str = crypto_utils.random_string(), longueur: float = 120.0, largeur: float = 120.0,
                         largeur_planche: float = 0.8, nb_planches: int = 8, type_id: int = 1,
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
                                               nom=nom, longueur=longueur, largeur=largeur, largeur_planche=largeur_planche, nb_planches=nb_planches, type_id=type_id)

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
        self._send_parcelle_and_check_response(expected_status_code=status.HTTP_201_CREATED)

    def test_ok_create_minimum(self):
        # On doit pouvoir créer une parcelle en donnant juste un nom
        self._send_parcelle_and_check_response(expected_status_code=status.HTTP_201_CREATED, largeur_planche=None, type_id=None, nb_planches=None)

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

    def test_nok_create_longueur_zero(self):
        self._send_parcelle_and_check_response(expected_status_code=status.HTTP_400_BAD_REQUEST, longueur=0)

    def test_nok_create_largeur_zero(self):
        self._send_parcelle_and_check_response(expected_status_code=status.HTTP_400_BAD_REQUEST, largeur=0)

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

    def test_nok_update_longueur_zero(self):
        self._update_parcelle(expected_status_code=status.HTTP_400_BAD_REQUEST, longueur=0)

    def test_nok_update_largeur_zero(self):
        self._update_parcelle(expected_status_code=status.HTTP_400_BAD_REQUEST, largeur=0)

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