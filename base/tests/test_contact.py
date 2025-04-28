from django.core import mail
from django.urls import reverse_lazy
from rest_framework import status

from base.models import User
from sebania.exceptions.error_code import ErrorCode
from sebania.tests.SebaniaTestCase import SebaniaTestCase
from sebania.utils import crypto_utils


class TestContact(SebaniaTestCase):
    url = reverse_lazy("contact-list")

    def test_contact_ok(self):
        email = crypto_utils.random_email()
        password = crypto_utils.generate_password()
        super_user = User.objects.create_superuser(email=email, password=password, first_name="Superuser", last_name="Superuser")
        self.init_current_user()
        sujet = crypto_utils.random_string()
        message = crypto_utils.random_string(length=600)
        request = {
            "sujet": sujet,
            "message": message,
        }
        response = self.client.post(self.url, request, format="json", headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Vérification de l'envoi d'un email
        emails = mail.outbox
        self.assertEqual(len(emails), 1)
        email = emails[0]
        self.assertEqual(email.to[0], super_user.email)
        self.assertIn(message, email.body)
        self.assertIn(sujet, email.body)

    def test_contact_nok_message_empty(self):
        self.init_current_user()
        request = {
            "sujet": crypto_utils.random_string(),
        }
        response = self.client.post(self.url, request, format="json", headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.check_error_response(response, ErrorCode.CONTACT_MESSAGE_EMPTY)
