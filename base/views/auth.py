from django.contrib.auth import logout
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from base.serializers.dto.auth import RegisterUserSerializer, ChangePasswordSerializer
from base.serializers.user import UserSerializer
from sebania.errors.auth import change_password_wrong_old_password_response


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
        old_password = request.data['old_password']
        new_password = request.data['new_password']
        user = self.request.user
        if not user.check_password(old_password):
            return change_password_wrong_old_password_response
        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_200_OK)