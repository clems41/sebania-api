from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from base.models import User
from base.serializers.ferme import FermeSerializer
from base.validators.user import validate_email
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from sebania.utils import email_utils, crypto_utils

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def change_password(self, request):
        self.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(self.data['old_password']):
            raise CustomException(ErrorCode.USER_OLD_PASSWORD_INCORRECT)
        user.set_password(self.data['new_password'])
        user.save()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.SerializerMethodField()

    def get_email(self, obj):
        return self.context['request'].query_params.get('email')

    def reset_password(self):
        self.is_valid(raise_exception=True)
        user = User.objects.get(email=self.data['email'])
        new_password = crypto_utils.generate_password()
        user.set_password(new_password)
        user.save()
        email_utils.send_reset_password(user, new_password)


class RegisterUserSerializer(ModelSerializer):
    ferme = FermeSerializer()

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'ferme']

    def is_valid(self, raise_exception=False):
        email_responsable = self.initial_data.get('email')
        validate_email(email_responsable)
        employes = self.initial_data.get("ferme").get('employes')
        if employes is not None:
            for employe in employes:
                employe_email = employe.get("email")
                validate_email(employe_email)
        return super().is_valid(raise_exception=raise_exception)

    @transaction.atomic
    def create(self, validated_data, **kwargs):
        # Récupération des données de la ferme
        ferme_data = validated_data.pop('ferme')

        # Création du responsable et ajout du groupe RESPONSABLE
        responsable = User.objects.create_responsable(email=validated_data['email'], password=validated_data['password'],
                                                      first_name=validated_data['first_name'], last_name=validated_data['last_name'])

        # Création de la ferme et des employés
        ferme = FermeSerializer(data=ferme_data, context={"responsable_id": responsable.id}) # requis, car non précisé dans la requête
        ferme.is_valid(raise_exception=True)
        ferme.save()

        return responsable
