from typing import List

from django.core.serializers import serialize
from django.db import transaction
from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ViewSet

from base.models import User, Ferme, MethodeAgricole
from base.serializers.user import UserSerializer

class MethodeAgricoleSerializer(ModelSerializer):
    class Meta:
        model = MethodeAgricole
        fields = ['id']

class EmployeSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']

class FermeSerializer(ModelSerializer):
    employes = EmployeSerializer(many=True)
    methodes_agricoles = serializers.ListField(
        child=serializers.IntegerField(),
    )
    class Meta:
        model = Ferme
        fields = ["nom", "adresse", "superficie_cultivee", "employes", "responsable_id", "methodes_agricoles"]

class RegisterUserSerializer(ModelSerializer):
    ferme = FermeSerializer()
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'ferme']

    @transaction.atomic
    def create(self, validated_data, **kwargs):
        responsable = User.objects.create_user(email=validated_data['email'], password=validated_data['password'], first_name=validated_data['first_name'], last_name=validated_data['last_name'])
        ferme_data = validated_data["ferme"]
        ferme = Ferme.objects.create(nom=ferme_data['nom'], adresse=ferme_data['adresse'], responsable_id=responsable.id, superficie_cultivee=ferme_data['superficie_cultivee'])
        employes = ferme_data["employes"]
        methodes_agricoles = ferme_data['methodes_agricoles']
        for employe in employes:
            password = "toto"
            new_employe = User.objects.create_user(email=employe['email'], password=password,
                                     first_name=employe['first_name'], last_name=employe['last_name'])
            ferme.employes.add(new_employe)
        for methode_id in methodes_agricoles:
            methode = MethodeAgricole.objects.get(id=methode_id)
            ferme.methodes.add(methode)
        ferme.save()
        return responsable

class RegisterUserResponseSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']


class AuthViewSet(ViewSet):
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'], url_path='register', serializer_class=RegisterUserSerializer, permission_classes=[], authentication_classes=[])
    def register_user(self, request):
        register_user_data = self.serializer_class(data=request.data)
        register_user_data.is_valid(raise_exception=True)
        register_user_data.save()
        return Response(status=status.HTTP_201_CREATED)