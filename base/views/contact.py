from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from base.serializers.contact import SendFeedbackSerializer


class ContactViewSet(GenericViewSet):
    serializer_class = SendFeedbackSerializer
    queryset = None

    @extend_schema(description="Envoi d'un retour utilisateur aux équipes Sebania")
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.send_feedback(self.request.user)
        return Response(status=status.HTTP_201_CREATED)