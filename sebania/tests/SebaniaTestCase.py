import json

from django.core import mail
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APITransactionTestCase

from base.models import User
from sebania.utils import crypto_utils
from sebania.exceptions.custom_exception import CustomException


class SebaniaTestCase(APITransactionTestCase):
    fixtures = ["activite_default", "culture_default", "methode_agricole", "type_parcelle", "unite", "auth_group"]
    current_user = None
    current_user_credentials = (None, None)

    def get_current_user(self):
        return self.current_user

    def get_current_user_credentials(self):
        return self.current_user_credentials

    def init_current_user(self, email = crypto_utils.random_email(), password = crypto_utils.generate_password()):
        user = User.objects.create_user(email=email, password=password,
                                        first_name=crypto_utils.random_string(), last_name=crypto_utils.random_string())
        self.assertIsNotNone(user)
        self.assertTrue(self.client.login(email=email, password=password))
        self.current_user = user
        self.current_user_credentials = (email, password)
        return user

    def get_jwt_headers(self, email = None, password= None):
        if email is None or password is None:
            if self.current_user is None:
                self.init_current_user()
            email, password = self.get_current_user_credentials()
        request = {
            "email": email,
            "password": password,
        }
        url = reverse_lazy('get_access_token')
        response = self.client.post(url, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.json()['access']
        self.assertIsNotNone(access_token)
        return {"Authorization": "Bearer " + access_token}

    def get_password_received_from_email(self, user_email: str) -> str:
        emails = mail.outbox
        self.assertTrue(len(emails) > 0)
        matches = [e for e in emails if e.to[0] == user_email]
        self.assertEqual(len(matches), 1)
        email_body = matches[0].body
        start_password = email_body.find('<td> ') + len('<td> ')
        stop_password = email_body.find(' </td>')
        return email_body[start_password: stop_password]

    def check_error_response(self, response, expected_exception: CustomException):
        response_data = json.loads(response.content)
        self.assertEqual(response_data.get("code"), expected_exception.code.value)
        self.assertEqual(response_data.get("message"), expected_exception.message)