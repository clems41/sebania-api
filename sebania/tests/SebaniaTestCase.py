import json

from django.core import mail
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APITransactionTestCase

from base.models import User
from sebania.exceptions.error_code import ErrorCode
from sebania.utils import crypto_utils


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

    def check_error_response(self, response, expected_error: ErrorCode, *args, **kwargs):
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, expected_error.value[1])
        self.assertEqual(response_data.get("code"), expected_error.name)
        self.assertEqual(response_data.get("message"), expected_error.value[0].format(*args, **kwargs))

    def check_response(self, expected: dict, response, request: dict):
        for actual_key, actual_value in response.items():
            self.assertTrue(actual_key in expected, "La clé '{}' existe dans la réponse, mais n'est pas attendue".format(actual_key))
            expected_value = expected.get(actual_key)

            # Cas d'une valeur à ne pas checker
            if type(expected_value) is str and expected_value == "no_check":
                continue

            # Cas d'une valeur à reprendre de la requête
            if type(expected_value) is str and "{request}." in expected_value:
                key_from_request = expected_value[len("{request}."):]
                self.assertTrue(key_from_request in request, "La clé '{}' n'a pas été trouvée dans la requête".format(key_from_request))
                value_from_request = request.get(key_from_request)
                self.assertEqual(value_from_request, actual_value)
                continue

            self.assertEqual(type(expected_value), type(actual_value), "Les types ne correspondent pas pour la clé '{}'".format(actual_key))

            # Cas d'un objet
            if type(expected_value) is dict:
                self.check_response(expected_value, actual_value, request=request)

            # Cas d'une liste
            elif type(expected_value) is list:
                self.assertEqual(len(expected_value), len(actual_value), "Les tailles de liste pour la clé '{}' ne correspondent pas".format(actual_key))
                for idx, expected_element in enumerate(expected_value):
                    actual_element = actual_value[idx]
                    if type(expected_element) is dict:
                        self.check_response(expected_element, actual_element, request=request)
                    else:
                        self.assertEqual(expected_element, actual_element)
            else:
                self.assertEqual(expected_value, actual_value)

    def check_entity(self, expected: dict, instance, request: dict):
        pass # TODO
