from django.contrib.auth.models import Group
from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from base.models import User
from base.serializers.ferme import FermeSerializer


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class RegisterUserSerializer(ModelSerializer):
    ferme = FermeSerializer()

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'ferme']

    @transaction.atomic
    def create(self, validated_data, **kwargs):
        # Récupération des données de la ferme
        ferme_data = validated_data.pop('ferme')

        # Création du responsable et ajout du groupe RESPONSABLE
        responsable = User.objects.create_user(**validated_data)
        responsable_group = Group.objects.get(name='RESPONSABLE')
        responsable_group.user_set.add(responsable)

        # Création de la ferme et des employés
        ferme_data['responsable_id'] = responsable.id # requis, car non précisé dans la requête
        ferme = FermeSerializer(data=ferme_data)
        ferme.is_valid(raise_exception=True)
        ferme.save()

        return responsable
