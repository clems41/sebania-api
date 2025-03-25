from django.contrib.auth.models import Group
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from base.models import User
from base.serializers.ferme import FermeSerializer
from sebania.services import email_service, crypto_service


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def change_password(self, request):
        self.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(self.data['old_password']):
            raise ValidationError("L'ancien mot de passe ne correspond pas")
        user.set_password(self.data['new_password'])
        user.save()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.SerializerMethodField()

    def get_email(self, obj):
        return self.context['request'].query_params.get('email')

    def reset_password(self):
        self.is_valid(raise_exception=True)
        user = User.objects.get(email=self.data['email'])
        new_password = crypto_service.generate_password()
        user.set_password(new_password)
        user.save()
        email_service.send_reset_password(user, new_password)


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
