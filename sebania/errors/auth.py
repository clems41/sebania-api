from rest_framework import status
from rest_framework.response import Response

change_password_wrong_old_password_response = (
    Response({"error": "L'ancien mot de passe ne correspond pas"}, status.HTTP_400_BAD_REQUEST))
