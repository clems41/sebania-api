from django.db import transaction
from rest_framework import serializers

from base.models import Activite, ActiviteFerme
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from sebania.utils.db_utils import get_one_or_raise_exception


class ActiviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activite
        fields = ['id', 'nom', 'need_culture']

class ActiviteFermeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='activite.id')
    nom = serializers.CharField(source='activite.nom', read_only=True)
    mots_cles = serializers.CharField(source='activite.mots_cles', read_only=True)
    need_culture = serializers.BooleanField(source='activite.need_culture', read_only=True)
    class Meta:
        model = ActiviteFerme
        fields = ['id', 'nom', 'categorie', 'mots_cles', 'need_culture']

    def validate_id(self, value):
        get_one_or_raise_exception(Activite, CustomException(ErrorCode.ACTIVITE_NOT_FOUND, value), id=value)
        return value

class UpdateActiviteFermeSerializer(serializers.Serializer):
    activites = ActiviteFermeSerializer(many=True)

    @transaction.atomic
    def create(self, validated_data):
        ferme = self.context.get('ferme')
        result = []
        # Cleanup old association
        ActiviteFerme.objects.filter(ferme=ferme).delete()

        # Create new association
        for activite in validated_data.pop('activites'):
            activite_id = activite.pop('activite').pop('id')
            categorie = activite.pop('categorie')
            activite_ferme = ActiviteFerme.objects.create(ferme=ferme, activite_id=activite_id, categorie=categorie)
            result.append(activite_ferme)
        return result