from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from base.models import MethodeAgricole, User, Ferme, Culture, CultureFerme, ActiviteFerme, Activite
from base.serializers.user import UserSerializer
from base.validators.user import validate_email
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from sebania.utils import email_utils


class MethodeAgricoleSerializer(ModelSerializer):
    class Meta:
        model = MethodeAgricole
        fields = '__all__'


class EmployeSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']

    def is_valid(self, raise_exception=False):
        email = self.initial_data.get('email')
        validate_email(email)
        return super().is_valid(raise_exception=raise_exception)

    def create(self, validated_data, **kwargs):
        ferme = self.context.get('ferme')
        employe, password = User.objects.create_employe(email=validated_data['email'], first_name=validated_data['first_name'], last_name=validated_data['last_name'])
        ferme.employes.add(employe)
        email_utils.send_email_to_new_employe(ferme, employe, password)
        return employe


def _create_data(ferme: Ferme):
    """
    Créer les liste d'activités et de cultures pour la ferme
    """
    cultures_default = Culture.objects.filter(default=True).all()
    for culture_default in cultures_default:
        CultureFerme.objects.create(culture=culture_default, ferme=ferme, categorie=culture_default.categorie_default)
    activites_default = Activite.objects.filter(default=True).all()
    for activite_default in activites_default:
        ActiviteFerme.objects.create(activite=activite_default, ferme=ferme, categorie=activite_default.categorie_default)


class FermeSerializer(ModelSerializer):
    employes = EmployeSerializer(many=True, required=False)
    methodes_agricoles = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )

    class Meta:
        model = Ferme
        fields = ["nom", "adresse", "superficie_cultivee", "employes", "methodes_agricoles", "code_postal"]

    def validate_code_postal(self, value):
        if value is None:
            return None
        if len(value) != 5:
            raise CustomException(ErrorCode.FERME_CODE_POSTAL_INCORRECT, value)
        return value

    def create(self, validated_data, **kwargs):
        # Création de la ferme
        employes_data = validated_data.pop('employes', [])
        methodes_agricoles_ids = validated_data.pop('methodes_agricoles', [])
        ferme = Ferme.objects.create(**validated_data, responsable_id=self.context['responsable_id'])

        # Création des employés (avec rôle EMPLOYE) et ajout à la ferme
        for emp_data in employes_data:
            employe = EmployeSerializer(data=emp_data, context={"ferme": ferme})
            employe.is_valid(raise_exception=True)
            employe.save()

        # Ajout des méthodes agricoles
        methodes_agricoles = MethodeAgricole.objects.filter(id__in=methodes_agricoles_ids)
        ferme.methodes.set(methodes_agricoles)
        _create_data(ferme)
        return ferme


class FermeViewSerializer(ModelSerializer):
    methodes = MethodeAgricoleSerializer(many=True)
    responsable = UserSerializer(read_only=True)
    employes = EmployeSerializer(many=True)
    class Meta:
        model = Ferme
        fields = ["id", "nom", "adresse", "superficie_cultivee", "employes", "responsable", "methodes", "code_postal"]


class UpdateFermeSerializer(ModelSerializer):
    methodes_agricoles = serializers.ListField(
        child=serializers.IntegerField(),
    )
    class Meta:
        model = Ferme
        fields = ["nom", "adresse", "superficie_cultivee", "methodes_agricoles"]