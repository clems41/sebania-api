import copy
import json

from django.contrib.auth.models import Group
from django.core import mail
from django.urls import reverse_lazy
from rest_framework import status

from base.models import User, Ferme, Culture, Activite
from sebania.tests import test_fixtures
from sebania.utils import crypto_utils
from sebania.tests.SebaniaTestCase import SebaniaTestCase
from base.tests.data.auth import register_user_request_0employes, register_user_request_2employes


class AuthResetPasswordTestCase(SebaniaTestCase):
    url = reverse_lazy('auth-reset-password')

    def test_ok_reset_password(self):
        # Create user
        user = self.init_current_user()

        # Ask for reset password
        request = {"email": user.email}
        response = self.client.get(self.url, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that email has been sent to user
        self.assertEqual(len(mail.outbox), 1)

        # Check that user can log with his new password
        new_password = self.get_password_received_from_email(user.email)
        self.assertTrue(self.client.login(email=user.email, password=new_password))


class AuthChangePasswordTestCase(SebaniaTestCase):
    url = reverse_lazy('auth-change-password')

    def test_ok_change_password(self):
        new_password = crypto_utils.generate_password()

        # Create user
        self.init_current_user()
        email, old_password = self.get_current_user_credentials()

        # Update password
        request = {
            "old_password": old_password,
            "new_password": new_password
        }
        response = self.client.put(self.url, request, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that user can log with new password and not with old one
        self.assertTrue(self.client.login(email=email, password=new_password), "User cannot log with new password")
        self.assertFalse(self.client.login(email=email, password=old_password), "User should not be able to log with old password")

    def test_nok_update_password_wrong_old_password(self):
        wrong_old_password = crypto_utils.generate_password()
        new_password = crypto_utils.generate_password()

        # Create user with old_password
        self.init_current_user()

        # Try to update password with wrong old one
        request = {
            "old_password": wrong_old_password,
            "new_password": new_password
        }
        response = self.client.put(self.url, request, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



class AuthRegisterTestCase(SebaniaTestCase):
    url = reverse_lazy('auth-register')

    def test_creation_data_after_register(self):
        # envoi requête pour enregistrer le responsable, la ferme et les employés
        create_ferme_request = register_user_request_2employes
        request_data = json.dumps(create_ferme_request)
        responsable_email = create_ferme_request.get('email')
        responsable_password = create_ferme_request.get('password')
        email_employe1 = create_ferme_request.get('ferme').get('employes')[0].get('email')
        email_employe2 = create_ferme_request.get('ferme').get('employes')[1].get('email')
        response = self.client.post(self.url, request_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # vérification que le responsable a bien une liste de cultures et d'activités associées à sa ferme
        responsable_headers = self.get_jwt_headers(email=responsable_email, password=responsable_password)
        activites_default = Activite.objects.filter(default=True).all()
        self._get_list_and_compare_with_activites_list(responsable_headers, activites_default)
        cultures_default = Culture.objects.filter(default=True).all()
        self._get_list_and_compare_with_cultures_list(responsable_headers, cultures_default)

        # récupération des mots de passe des employés pour l'authentification
        password_employe1 = self.get_password_received_from_email(email_employe1)
        password_employe2 = self.get_password_received_from_email(email_employe2)
        headers_employe1 = self.get_jwt_headers(email=email_employe1, password=password_employe1)
        headers_employe2 = self.get_jwt_headers(email_employe2, password=password_employe2)

        # vérification que les employés ont bien une liste de cultures et d'activités associées à la ferme
        self._get_list_and_compare_with_cultures_list(headers_employe1, cultures_default)
        self._get_list_and_compare_with_cultures_list(headers_employe2, cultures_default)
        self._get_list_and_compare_with_activites_list(headers_employe1, activites_default)
        self._get_list_and_compare_with_activites_list(headers_employe2, activites_default)


    def _get_list_and_compare_with_activites_list(self, headers, default_list):
        activites_url = reverse_lazy('fermes-activites')
        response = self.client.get(activites_url, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_list = json.loads(response.content).get('activites')
        self.assertEqual(len(response_list), len(default_list))
        response_list_set = set((elem.get('id'), elem.get('nom'), elem.get('categorie')) for elem in response_list)
        for elem in default_list:
            self.assertIn((elem.id, elem.nom, elem.categorie_default), response_list_set)


    def _get_list_and_compare_with_cultures_list(self, headers, default_list):
        cultures_url = reverse_lazy('fermes-get-cultures')
        response = self.client.get(cultures_url, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_list = json.loads(response.content)
        self.assertEqual(len(response_list), len(default_list))
        response_list_set = set((elem.get('id'), elem.get('nom'), elem.get('categorie')) for elem in response_list)
        for elem in default_list:
            self.assertIn((elem.id, elem.nom, elem.categorie_default), response_list_set)


    def test_ok_register_avec_employes(self):
        self._test_register(register_user_request_2employes)

    def test_ok_register_sans_employes(self):
        self._test_register(register_user_request_0employes)

    def test_nok_email_responsable_already_exist(self):
        email_responsable = register_user_request_0employes.get("email")
        test_fixtures.create_user(email=email_responsable)
        self._test_register(register_user_request_0employes, expected_status_code=status.HTTP_409_CONFLICT)

    def test_nok_email_employe_already_exist(self):
        email_employe = register_user_request_2employes.get("ferme").get("employes")[0].get("email")
        test_fixtures.create_user(email=email_employe)
        self._test_register(register_user_request_2employes, expected_status_code=status.HTTP_409_CONFLICT)

    def test_nok_code_postal_incorrect(self):
        request = copy.deepcopy(register_user_request_0employes)
        invalid_code_postaux = ["25", "4152", "123456", "0"]
        for invalid_code_postal in invalid_code_postaux:
            request["ferme"]["code_postal"] = invalid_code_postal
            self._test_register(request, expected_status_code=status.HTTP_400_BAD_REQUEST)

    def _test_register(self, request, expected_status_code: int = status.HTTP_201_CREATED):
        # envoi requête pour enregistrer le responsable, la ferme et les employés
        request_data = json.dumps(request)
        responsable_password = request.get('password')
        responsable_email = request.get('email')
        response = self.client.post(self.url, request_data, content_type="application/json")
        self.assertEqual(response.status_code, expected_status_code)

        if expected_status_code != status.HTTP_201_CREATED:
            return
        # verification de la création du responsable et de son rôle RESPONSABLE
        response_data = json.loads(response.content)
        responsable_id = response_data.get('id')
        responsable = User.objects.get(id=responsable_id)
        responsable_group = Group.objects.get(name='RESPONSABLE')
        self.assertIsNotNone(responsable)
        self.assertEqual(responsable.first_name, response_data.get('first_name'))
        self.assertEqual(responsable.last_name, response_data.get('last_name'))
        self.assertEqual(responsable.email, response_data.get('email'))
        self.assertTrue(responsable_group.user_set.filter(id=responsable.id).exists())

        # verification que le responsable peut s'authentifier avec son mot de passe
        self.assertTrue(self.client.login(email=responsable_email, password=responsable_password))

        # verification de la création de la ferme
        ferme_request_data = request.get('ferme')
        ferme = Ferme.objects.get(responsable_id=responsable_id)
        self.assertIsNotNone(ferme)
        self.assertEqual(ferme.nom, ferme_request_data.get('nom'))
        self.assertEqual(ferme.adresse, ferme_request_data.get('adresse'))
        self.assertEqual(ferme.superficie_cultivee, ferme_request_data.get('superficie_cultivee'))

        # verification que les méthodes agricoles ont bien été
        methodes_ids = ferme_request_data.get('methodes_agricoles')
        for methode in ferme.methodes.all():
            self.assertTrue(methode.id in methodes_ids)

        employes_data = ferme_request_data.get('employes')
        if employes_data is not None and len(employes_data) > 0:
            # verification de la création des employés, qu'ils ont le rôle EMPLOYE et qu'ils peuvent se connecter avec le mdp reçu par mail
            employe_group = Group.objects.get(name='EMPLOYE')
            for employe_data in employes_data:
                employe = User.objects.get(email=employe_data.get('email'))
                self.assertIsNotNone(employe)
                self.assertEqual(employe.first_name, employe_data.get('first_name'))
                self.assertEqual(employe.last_name, employe_data.get('last_name'))
                self.assertTrue(employe_group.user_set.filter(id=employe.id).exists())
                password = self.get_password_received_from_email(employe.email)
                self.assertTrue(self.client.login(email=employe.email, password=password))