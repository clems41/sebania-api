from django.contrib.auth import logout
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from base.models import User
from base.serializers.dto.auth import RegisterUserSerializer, ChangePasswordSerializer, ResetPasswordSerializer
from base.serializers.user import UserSerializer


class AuthViewSet(ViewSet):
    serializer_class = None

    @extend_schema(responses=UserSerializer,
                   description="Créer un compte pour un nouvel utilisateur, avec création de la ferme et des comptes utilisateurs des employés")
    @action(detail=False, methods=['post'], url_path='register', serializer_class=RegisterUserSerializer,
            permission_classes=[], authentication_classes=[], url_name="register", basename="auth-register",
            schema="")
    def register_user(self, request):
        register_user_data = self.serializer_class(data=request.data)
        register_user_data.is_valid(raise_exception=True)
        responsable = register_user_data.save()
        serializer = UserSerializer(responsable)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['put'], url_path='logout', serializer_class=None, url_name="logout", basename="auth-logout")
    def logout(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)

    @extend_schema(responses=None,
                   description="Modification du mot de passe de l'utilisateur authentifié à partir de son ancien mot de passe")
    @action(detail=False, methods=['put'], url_path='change-password', serializer_class=ChangePasswordSerializer, url_name="change-password", basename="auth-change-password")
    def change_password(self, request):
        form = self.serializer_class(data=request.data)
        form.change_password(request)
        return Response(status=status.HTTP_200_OK)

    @extend_schema(responses=None,
                   description="En cas de mot de passe perdu : envoi d'un email à l'utilisateur avec un mot de passe temporaire")
    @action(detail=False, methods=['get'], url_path='reset-password', serializer_class=ResetPasswordSerializer,
            permission_classes=[], authentication_classes=[], url_name="reset-password", basename="auth-reset-password")
    def reset_password(self, request):
        form = self.serializer_class(data=request.data, context={'request': request})
        form.reset_password()
        return Response(status=status.HTTP_200_OK)