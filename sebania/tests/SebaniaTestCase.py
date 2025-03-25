from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APITransactionTestCase

from base.models import User
from sebania.services import crypto_service


class SebaniaTestCase(APITransactionTestCase):
    fixtures = ["activite_default", "culture_default", "methode_agricole", "type_parcelle", "unite", "auth_group"]
    current_user = None
    current_user_credentials = (None, None)

    def get_current_user(self):
        return self.current_user

    def get_current_user_credentials(self):
        return self.current_user_credentials

    def init_current_user(self, email = "example@gmail.com", password = crypto_service.generate_password()):
        user = User.objects.create_user(email=email, password=password, first_name="Toto", last_name="Tata")
        self.assertIsNotNone(user)
        self.assertTrue(self.client.login(email=email, password=password))
        self.current_user = user
        self.current_user_credentials = (email, password)
        return user

    def get_jwt_headers(self, user: User = None):
        if user is None:
            if self.current_user is None:
                self.init_current_user()
        url = reverse_lazy('get_access_token')
        email, password = self.get_current_user_credentials()
        request = {
            "email": email,
            "password": password,
        }
        response = self.client.post(url, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.json()['access']
        self.assertIsNotNone(access_token)
        return {"Authorization": "Bearer " + access_token}