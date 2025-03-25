import json

from django.contrib.auth.models import Group
from django.core import mail
from django.urls import reverse_lazy
from rest_framework import status

from base.models import User, Ferme
from sebania.services import crypto_service
from sebania.tests.SebaniaTestCase import SebaniaTestCase
from base.tests.data.auth import register_user_request_0employes, register_user_request_2employes


class AuthResetPasswordTestCase(SebaniaTestCase):
    url = reverse_lazy('auth-reset-password')

    def test_reset_password_ok(self):
        # Create user
        user = self.init_current_user()

        # Ask for reset password
        request = {"email": user.email}
        response = self.client.get(self.url, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that email has been sent to user
        self.assertEqual(len(mail.outbox), 1)

        # Check that user can log with his new password
        email_received = mail.outbox[0]
        start_password = email_received.body.find('<td> ') + len('<td> ')
        stop_password = email_received.body.find(' </td>')
        new_password = email_received.body[start_password: stop_password]
        self.assertTrue(self.client.login(email=user.email, password=new_password))


class AuthChangePasswordTestCase(SebaniaTestCase):
    url = reverse_lazy('auth-change-password')

    def test_change_password_ok(self):
        new_password = crypto_service.generate_password()

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

    def test_update_password_nok_wrong_old_password(self):
        wrong_old_password = crypto_service.generate_password()
        new_password = crypto_service.generate_password()

        # Create user with old_password
        self.init_current_user()

        # Try to update password with wrong old one
        request = {
            "old_password": wrong_old_password,
            "new_password": new_password
        }
        response = self.client.put(self.url, request, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



class AuthRegisterTestCase(SebaniaTestCase):
    url = reverse_lazy('auth-register')

    def test_register_avec_employes_ok(self):
        self._test_register(register_user_request_2employes)

    def test_register_sans_employes_ok(self):
        self._test_register(register_user_request_0employes)

    def _test_register(self, request):
        # envoi requête pour enregistrer le responsable, la ferme et les employés
        request_data = json.dumps(request)
        responsable_password = request.get('password')
        response = self.client.post(self.url, request_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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
        self.assertTrue(self.client.login(email=response_data.get('email'), password=responsable_password))

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
        if len(employes_data) > 0:
            # verification de la création des employés et qu'ils ont le rôle EMPLOYE
            employe_group = Group.objects.get(name='EMPLOYE')
            for employe_data in employes_data:
                employe = User.objects.get(email=employe_data.get('email'))
                self.assertIsNotNone(employe)
                self.assertEqual(employe.first_name, employe_data.get('first_name'))
                self.assertEqual(employe.last_name, employe_data.get('last_name'))
                self.assertTrue(employe_group.user_set.filter(id=employe.id).exists())

            # verification que les employés ont reçu un mail avec leur mot de passe et qu'ils peuvent se connecter
            emails = mail.outbox
            self.assertEqual(len(emails), len(employes_data))
            for email in emails:
                email_employe = email.to[0]
                start_password = email.body.find('<td> ') + len('<td> ')
                stop_password = email.body.find(' </td>')
                password = email.body[start_password: stop_password]
                self.assertTrue(self.client.login(email=email_employe, password=password))
