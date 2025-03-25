from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APITransactionTestCase

class SebaniaTestCase(APITransactionTestCase):
    fixtures = ["activite_default", "culture_default", "methode_agricole", "type_parcelle", "unite", "auth_group"]

    def _get_jwt_headers(self, email: str, password: str):
        url = reverse_lazy('get_access_token')
        request = {
            "email": email,
            "password": password,
        }
        response = self.client.post(url, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.json()['access']
        self.assertIsNotNone(access_token)
        return {"Authorization": "Bearer " + access_token}