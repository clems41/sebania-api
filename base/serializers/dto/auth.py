import secrets
import string

from django.contrib.auth.models import Group
from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from base.models import MethodeAgricole, User, Ferme
from services import email_service


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


def _generate_password():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(12))  # mot de passe de longueur 12

def _send_email_to_new_employe(responsable: User, ferme: Ferme, employe: User, employe_password: str):
    subject = "Bienvenue sur sebania"
    template_context = {
        "employe_prenom": employe.first_name,
        "responsable_prenom": responsable.first_name,
        "nom_ferme": ferme.nom,
        "app_url": "TODO",
        "password_employe": employe_password,
    }
    template_name = "emails/send-employe-password.html"
    email_service.send_email(subject, employe.email, template_name, template_context)


class RegisterUserSerializer(ModelSerializer):
    ferme = FermeSerializer()

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'ferme']

    @transaction.atomic
    def create(self, validated_data, **kwargs):
        # Récupération des données de la ferme
        ferme_data = validated_data.pop('ferme')
        employes_data = ferme_data.pop('employes', [])
        methodes_agricoles_ids = ferme_data.pop('methodes_agricoles', [])

        # Création du responsable et ajout du groupe RESPONSABLE
        password = validated_data.pop('password')
        responsable = User.objects.create_user(password=password, **validated_data)
        responsable_group = Group.objects.get(name='RESPONSABLE')
        responsable_group.user_set.add(responsable)

        # Création de la ferme
        ferme = Ferme.objects.create(responsable=responsable, **ferme_data)

        # Création des employés (avec rôle EMPLOYE) et ajout à la ferme
        employes = []
        employe_group = Group.objects.get(name='EMPLOYE')
        for emp_data in employes_data:
            emp_password=_generate_password()
            employe = User.objects.create_user(password=emp_password, **emp_data)
            employe_group.user_set.add(employe)
            employes.append(employe)
            _send_email_to_new_employe(responsable, ferme, employe, emp_password)

        ferme.employes.set(employes)  # Associer les employés à la ferme

        # Ajout des méthodes agricoles
        methodes_agricoles = MethodeAgricole.objects.filter(id__in=methodes_agricoles_ids)
        ferme.methodes.set(methodes_agricoles)

        return responsable
