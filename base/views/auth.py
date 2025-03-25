from django.contrib.auth import logout
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from base.serializers.dto.auth import RegisterUserSerializer
from base.serializers.user import UserSerializer


class AuthViewSet(ViewSet):
    serializer_class = None

    @action(detail=False, methods=['post'], url_path='register', serializer_class=RegisterUserSerializer,
            permission_classes=[], authentication_classes=[], url_name="register", basename="auth-register")
    def register_user(self, request):
        register_user_data = self.serializer_class(data=request.data)
        register_user_data.is_valid(raise_exception=True)
        responsable = register_user_data.save()
        serializer = UserSerializer(responsable)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='logout', serializer_class=None, url_name="logout", basename="auth-logout")
    def logout(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)