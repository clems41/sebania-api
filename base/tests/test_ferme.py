import json

from django.urls import reverse_lazy, reverse
from rest_framework import status

from base.models import Ferme
from sebania.tests import test_fixtures
from sebania.tests.SebaniaTestCase import SebaniaTestCase
from sebania.utils import crypto_utils


class UpdateFermeDetailsTestCase(SebaniaTestCase):
    url = reverse_lazy('fermes-update-ferme-details')

    def _send_request_and_check_response(self, expected_status_code=status.HTTP_200_OK):
        new_nom = crypto_utils.random_string()
        new_adresse = crypto_utils.random_string()
        new_superficie = 3000
        new_methodes_agricoles = [1]
        new_code_postal = 98800
        request = {
            "methodes_agricoles": new_methodes_agricoles,
            "nom": new_nom,
            "adresse": new_adresse,
            "superficie_cultivee": new_superficie,
            "code_postal": new_code_postal,
        }
        response = self.client.put(self.url, request, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, expected_status_code)

        # Vérification de la réponse
        if expected_status_code == status.HTTP_200_OK:
            response_data = json.loads(response.content)
            self.assertEqual(response_data.get('nom'), request.get('nom'))
            self.assertEqual(response_data.get('adresse'), request.get('adresse'))
            self.assertEqual(response_data.get('superficie'), request.get('superficie'))
            self.assertEqual(len(response_data.get('methodes_agricoles')), 1)
            self.assertEqual(response_data.get('methodes_agricoles')[0].get("id"), request.get("methodes_agricoles")[0])

    def test_ok_update_ferme_details(self):
        # Création du responsable et de la ferme et des employés
        responsable = self.init_current_user()
        test_fixtures.create_ferme(responsable)

        # Modification de la ferme
        self._send_request_and_check_response()

    def test_nok_update_ferme_details_as_employe(self):
        # Création du responsable et de la ferme et des employés
        responsable = test_fixtures.create_user()
        employes = [self.init_current_user(),
                    test_fixtures.create_user()]  # le user qui va s'authentifier fait partie des employés et non responsable
        test_fixtures.create_ferme(responsable, employes)

        # Modification de la ferme
        self._send_request_and_check_response(expected_status_code=status.HTTP_403_FORBIDDEN)


class FermeDeleteEmployeTestCase(SebaniaTestCase):
    def test_ok_delete_employee_then_add_employe_with_same_email(self):
        # Création du responsable et de la ferme et des employés
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable)
        nb_init_employe = ferme.employes.count()

        # Suppresion d'un employé
        employe = ferme.employes.first()
        url = reverse('fermes-delete-employe', kwargs={'user_id': employe.id})
        response = self.client.delete(url, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Vérification que l'utilisateur a été supprimé
        ferme = Ferme.objects.get(id=ferme.id)
        self.assertEqual(ferme.employes.count(), nb_init_employe - 1)

        # Ajout d'un nouvel employé avec le même email
        request = {
            "email": employe.email,
            "first_name": employe.first_name,
            "last_name": employe.last_name,
        }
        url = reverse_lazy('fermes-add-employe')
        response = self.client.post(url, request, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Vérification que l'utilisateur a bien été ajouté
        ferme = Ferme.objects.get(id=ferme.id)
        self.assertEqual(ferme.employes.count(), nb_init_employe)

    def test_ok_delete_employe(self):
        # Création du responsable et de la ferme et des employés
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable)

        # Suppresion d'un employé
        employe_id = ferme.employes.first().id
        url = reverse('fermes-delete-employe', kwargs={'user_id': employe_id})
        response = self.client.delete(url, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Vérification de la réponse
        response_data = json.loads(response.content)
        self.assertEqual(response_data.get('id'), ferme.id)
        self.assertEqual(response_data.get('nom'), ferme.nom)
        self.assertEqual(response_data.get('adresse'), ferme.adresse)
        self.assertEqual(response_data.get('superficie_cultivee'), ferme.superficie_cultivee)
        response_employes = response_data.get('employes')
        self.assertEqual(len(response_employes), 1)
        new_employe_found = False
        for employe in response_employes:
            if employe.get('id') == employe_id:
                new_employe_found = True
                break
        self.assertEqual(new_employe_found, False)

        # Vérification en base de données
        ferme_db = Ferme.objects.get(id=ferme.id)
        self.assertEqual(ferme_db.nom, ferme.nom)
        self.assertEqual(ferme_db.adresse, ferme.adresse)
        self.assertEqual(ferme_db.superficie_cultivee, ferme.superficie_cultivee)
        self.assertFalse(ferme_db.employes.filter(id=employe_id).exists())

    def test_nok_delete_employe_bad_permission(self):
        # Création du responsable et de la ferme et des employés
        responsable = test_fixtures.create_user()
        employes = [self.init_current_user(),
                    test_fixtures.create_user()]  # le user qui va s'authentifier fait partie des employés et non responsable
        ferme = test_fixtures.create_ferme(responsable, employes)

        # Suppresion d'un employé, mais en se connectant avec le compte employé
        employe_id = ferme.employes.last().id
        url = reverse_lazy('fermes-delete-employe', kwargs={'user_id': employe_id})
        response = self.client.delete(url, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_nok_delete_employe_pas_employe(self):
        # Création du responsable et de la ferme et des employés
        responsable = self.init_current_user()
        test_fixtures.create_ferme(responsable)
        user_pas_employe = test_fixtures.create_user()

        # Suppresion d'un utilisateur non employé de la ferme
        url = reverse_lazy('fermes-delete-employe', kwargs={'user_id': user_pas_employe.id})
        response = self.client.delete(url, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_nok_delete_employe_not_existing(self):
        # Création du responsable et de la ferme et des employés
        responsable = self.init_current_user()
        test_fixtures.create_ferme(responsable)

        # Suppresion d'un utilisateur qui n'existe pas
        url = reverse_lazy('fermes-delete-employe', kwargs={'user_id': 999})
        response = self.client.delete(url, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FermeAddEmployeTestCase(SebaniaTestCase):
    url = reverse_lazy('fermes-add-employe')

    def test_ok_add_employe(self):
        # Création du responsable et de la ferme et des employés
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable)

        # Ajout d'un nouvel employé
        new_employe_email = crypto_utils.random_email()
        new_employe_first_name = crypto_utils.random_string()
        new_employe_last_name = crypto_utils.random_string()
        request = {
            "email": new_employe_email,
            "first_name": new_employe_first_name,
            "last_name": new_employe_last_name,
        }
        response = self.client.post(self.url, request, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Vérification de la réponse
        response_data = json.loads(response.content)
        self.assertEqual(response_data.get('id'), ferme.id)
        self.assertEqual(response_data.get('nom'), ferme.nom)
        self.assertEqual(response_data.get('adresse'), ferme.adresse)
        self.assertEqual(response_data.get('superficie_cultivee'), ferme.superficie_cultivee)
        response_employes = response_data.get('employes')
        self.assertEqual(len(response_employes), 3)
        new_employe_found = False
        for employe in response_employes:
            if employe.get('email') == new_employe_email:
                self.assertEqual(employe.get('first_name'), new_employe_first_name)
                self.assertEqual(employe.get('last_name'), new_employe_last_name)
                new_employe_found = True
                break
        self.assertEqual(new_employe_found, True)

        # Vérification en base de données
        ferme_db = Ferme.objects.get(id=ferme.id)
        self.assertEqual(ferme_db.nom, ferme.nom)
        self.assertEqual(ferme_db.adresse, ferme.adresse)
        self.assertEqual(ferme_db.superficie_cultivee, ferme.superficie_cultivee)
        new_employe = ferme_db.employes.filter(email=new_employe_email)
        self.assertTrue(new_employe.exists())
        self.assertEqual(new_employe.get().first_name, new_employe_first_name)
        self.assertEqual(new_employe.get().last_name, new_employe_last_name)

        # verification que le nouvel employé ait reçu un mail avec son mot de passe et qu'ils peuvent se connecter
        new_employe_password = self.get_password_received_from_email(new_employe_email)
        self.assertTrue(self.client.login(email=new_employe_email, password=new_employe_password))

    def test_nok_add_employe_bad_permission(self):
        # Création du responsable et de la ferme et des employés
        responsable = test_fixtures.create_user()
        employes = [self.init_current_user(),
                    test_fixtures.create_user()]  # le user qui va s'authentifier fait partie des employés et non responsable
        ferme = test_fixtures.create_ferme(responsable, employes)

        # Ajout d'un nouvel employé, mais en se connectant avec le compte employé
        new_employe_email = crypto_utils.random_email()
        new_employe_first_name = crypto_utils.random_string()
        new_employe_last_name = crypto_utils.random_string()
        request = {
            "email": new_employe_email,
            "first_name": new_employe_first_name,
            "last_name": new_employe_last_name,
        }
        response = self.client.post(self.url, request, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class ConfigurationFermeTestCase(SebaniaTestCase):
    url = None
    keyword = None

    def _send_request(self, request, expected_status_code: int = status.HTTP_200_OK):
        if self.get_current_user() is None:
            responsable = self.init_current_user()
            test_fixtures.create_ferme(responsable)
        response = self.client.put(self.url, data=json.dumps(request),
            content_type='application/json', headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, expected_status_code)

    def _get_working_request(self):
        categorie1 = crypto_utils.random_string()
        categorie2 = crypto_utils.random_string()
        categorie3 = crypto_utils.random_string()
        return {
            self.keyword: [
                {
                    "id": 1,
                    "categorie": categorie1
                },
                {
                    "id": 5,
                    "categorie": categorie1
                },
                {
                    "id": 8,
                    "categorie": categorie1
                },
                {
                    "id": 12,
                    "categorie": categorie2
                },
                {
                    "id": 15,
                    "categorie": categorie3
                },
            ]
        }

    def _get_second_request(self):
        categorie1 = crypto_utils.random_string()
        categorie2 = crypto_utils.random_string()
        return {
            self.keyword: [
                {
                    "id": 8,
                    "categorie": categorie1
                },
                {
                    "id": 9,
                    "categorie": categorie1
                },
                {
                    "id": 17,
                    "categorie": categorie1
                },
                {
                    "id": 13,
                    "categorie": categorie2
                },
                {
                    "id": 2,
                    "categorie": categorie1
                },
            ]
        }

    def _get_data(self):
        response = self.client.get(self.url, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return json.loads(response.content)

    def _check_data(self, request):
        data = self._get_data()[self.keyword]
        self.assertEqual(len(data), len(request[self.keyword]))
        for expected_data in request[self.keyword]:
            actual_data = next(actual_data for actual_data in data if actual_data['id'] == expected_data['id'])
            self.assertIsNotNone(actual_data)
            self.assertIsNotNone(actual_data['nom'])
            self.assertEqual(actual_data['categorie'], expected_data['categorie'])
            if self.keyword == "activites":
                self.assertIsNotNone(actual_data['mots_cles'])


class TestConfigurationActiviteFerme(ConfigurationFermeTestCase):
    url = reverse_lazy('fermes-activites')
    keyword = "activites"

    def test_activites_ok(self):
        request = self._get_working_request()
        self._send_request(request)
        self._check_data(request)

    def test_activites_ok_2updates(self):
        request = self._get_working_request()
        self._send_request(request)
        second_request = self._get_second_request()
        self._send_request(second_request)
        self._check_data(second_request)

    def test_activites_nok_activite_not_found(self):
        request = {
            "activites": [
                {
                    "id": 999,
                    "categorie": crypto_utils.random_string()
                }
            ]
        }
        self._send_request(request, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_activites_nok_categorie_empty(self):
        request = {
            "activites": [
                {
                    "id": 12,
                    "categorie": ""
                }
            ]
        }
        self._send_request(request, expected_status_code=status.HTTP_400_BAD_REQUEST)

    def test_activites_nok_employe_not_allowed(self):
        employe = self.init_current_user()
        responsable = test_fixtures.create_user()
        test_fixtures.create_ferme(responsable=responsable, employes=[employe])
        self._send_request(self._get_working_request(), expected_status_code=status.HTTP_403_FORBIDDEN)


class TestConfigurationCultureFerme(ConfigurationFermeTestCase):
    url = reverse_lazy('fermes-cultures')
    keyword = "cultures"

    def test_cultures_ok(self):
        request = self._get_working_request()
        self._send_request(request)
        self._check_data(request)

    def test_cultures_ok_2updates(self):
        request = self._get_working_request()
        self._send_request(request)
        second_request = self._get_second_request()
        self._send_request(second_request)
        self._check_data(second_request)

    def test_cultures_nok_culture_not_found(self):
        request = {
            "cultures": [
                {
                    "id": 999,
                    "categorie": crypto_utils.random_string()
                }
            ]
        }
        self._send_request(request, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_cultures_nok_categorie_empty(self):
        request = {
            "cultures": [
                {
                    "id": 12,
                    "categorie": ""
                }
            ]
        }
        self._send_request(request, expected_status_code=status.HTTP_400_BAD_REQUEST)

    def test_cultures_nok_employe_not_allowed(self):
        employe = self.init_current_user()
        responsable = test_fixtures.create_user()
        test_fixtures.create_ferme(responsable=responsable, employes=[employe])
        self._send_request(self._get_working_request(), expected_status_code=status.HTTP_403_FORBIDDEN)
