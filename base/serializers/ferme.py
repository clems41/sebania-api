from django.contrib.auth.models import Group
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from base.models import MethodeAgricole, User, Ferme
from sebania.services import crypto_service, email_service


class MethodeAgricoleSerializer(ModelSerializer):
    class Meta:
        model = MethodeAgricole
        fields = '__all__'


class EmployeSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']


class FermeSerializer(ModelSerializer):
    employes = EmployeSerializer(many=True)
    methodes_agricoles = serializers.ListField(
        child=serializers.IntegerField(),
    )
    responsable_id = serializers.IntegerField(required=False) # non requis lors de la réception de la requête car renseigné une fois qu'il a été créé en base de données

    class Meta:
        model = Ferme
        fields = ["nom", "adresse", "superficie_cultivee", "employes", "responsable_id", "methodes_agricoles"]

    def create(self, validated_data, **kwargs):
        # Création de la ferme
        responsable_id = validated_data.get('responsable_id')
        responsable = User.objects.get(id=responsable_id)
        employes_data = validated_data.pop('employes', [])
        methodes_agricoles_ids = validated_data.pop('methodes_agricoles', [])
        ferme = Ferme.objects.create(**validated_data)

        # Création des employés (avec rôle EMPLOYE) et ajout à la ferme
        employes = []
        employe_group = Group.objects.get(name='EMPLOYE')
        for emp_data in employes_data:
            emp_password= crypto_service.generate_password()
            employe = User.objects.create_user(password=emp_password, **emp_data)
            employe_group.user_set.add(employe)
            employes.append(employe)
            email_service.send_email_to_new_employe(responsable.first_name, ferme, employe, emp_password)

        ferme.employes.set(employes)  # Associer les employés à la ferme

        # Ajout des méthodes agricoles
        methodes_agricoles = MethodeAgricole.objects.filter(id__in=methodes_agricoles_ids)
        ferme.methodes.set(methodes_agricoles)
        return ferme