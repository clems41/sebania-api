import json

from django.core import mail
from django.urls import reverse_lazy, reverse
from rest_framework import status

from base.models import Ferme
from sebania.services import crypto_service
from sebania.tests import test_fixtures
from sebania.tests.SebaniaTestCase import SebaniaTestCase


class FermeDeleteEmployeTestCase(SebaniaTestCase):
    def test_delete_employe_ok(self):
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


    def test_delete_employe_nok_bad_permission(self):
        # Création du responsable et de la ferme et des employés
        responsable = test_fixtures.create_user()
        employes = [self.init_current_user(), test_fixtures.create_user()] # le user qui va s'authentifier fait partie des employés et non responsable
        ferme = test_fixtures.create_ferme(responsable, employes)

        # Suppresion d'un employé, mais en se connectant avec le compte employé
        employe_id = ferme.employes.last().id
        url = reverse_lazy('fermes-delete-employe', kwargs={'user_id': employe_id})
        response = self.client.delete(url, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_delete_employe_nok_pas_employe(self):
        # Création du responsable et de la ferme et des employés
        responsable = self.init_current_user()
        test_fixtures.create_ferme(responsable)
        user_pas_employe = test_fixtures.create_user()

        # Suppresion d'un utilisateur non employé de la ferme
        url = reverse_lazy('fermes-delete-employe', kwargs={'user_id': user_pas_employe.id})
        response = self.client.delete(url, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_delete_employe_nok_not_existing(self):
        # Création du responsable et de la ferme et des employés
        responsable = self.init_current_user()
        test_fixtures.create_ferme(responsable)

        # Suppresion d'un utilisateur qui n'existe pas
        url = reverse_lazy('fermes-delete-employe', kwargs={'user_id': 999})
        response = self.client.delete(url, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FermeAddEmployeTestCase(SebaniaTestCase):
    url = reverse_lazy('fermes-add-employe')

    def test_add_employe_ok(self):
        # Création du responsable et de la ferme et des employés
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable)

        # Ajout d'un nouvel employé
        new_employe_email = crypto_service.random_email()
        new_employe_first_name = crypto_service.random_string()
        new_employe_last_name = crypto_service.random_string()
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
        emails = mail.outbox
        self.assertEqual(len(emails), 1)
        email = emails[0]
        start_password = email.body.find('<td> ') + len('<td> ')
        stop_password = email.body.find(' </td>')
        password = email.body[start_password: stop_password]
        self.assertTrue(self.client.login(email=new_employe_email, password=password))


    def test_add_employe_nok_bad_permission(self):
        # Création du responsable et de la ferme et des employés
        responsable = test_fixtures.create_user()
        employes = [self.init_current_user(), test_fixtures.create_user()] # le user qui va s'authentifier fait partie des employés et non responsable
        ferme = test_fixtures.create_ferme(responsable, employes)

        # Ajout d'un nouvel employé, mais en se connectant avec le compte employé
        new_employe_email = crypto_service.random_email()
        new_employe_first_name = crypto_service.random_string()
        new_employe_last_name = crypto_service.random_string()
        request = {
            "email": new_employe_email,
            "first_name": new_employe_first_name,
            "last_name": new_employe_last_name,
        }
        response = self.client.post(self.url, request, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

