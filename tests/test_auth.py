import json

from django.contrib.auth.models import Group
from django.core import mail
from django.urls import reverse_lazy
from rest_framework import status

from base.models import User, Ferme
from tests.SebaniaTestCase import SebaniaTestCase
from tests.data.auth import register_user_request


# Create your tests here.
class AuthTestCase(SebaniaTestCase):

    def test_register_ok(self):
        # envoi requête pour enregistrer le responsable, la ferme et les employés
        url = reverse_lazy('auth-register')
        request = register_user_request
        request_data = json.dumps(request)
        responsable_password = request.get('password')
        response = self.client.post(url, request_data, content_type="application/json")
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

        # verification de la création des employés et qu'ils ont le rôle EMPLOYE
        employe_group = Group.objects.get(name='EMPLOYE')
        employes_data = ferme_request_data.get('employes')
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
            password = email.body[start_password : stop_password]
            self.assertTrue(self.client.login(email=email_employe, password=password))

