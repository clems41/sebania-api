from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from base.serializers.user import UserSerializer


# Create your views here.


class RegisterUser(GenericAPIView):
    permission_classes = []
    authentication_classes = []
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)