from django.db import transaction
from rest_framework import serializers

from base.models import Activite, ActiviteFerme
from base.serializers.unite import UniteSerializer
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from sebania.utils.db_utils import get_one_or_raise_exception


class ActiviteSerializer(serializers.ModelSerializer):
    unites = UniteSerializer(many=True, read_only=True)
    class Meta:
        model = Activite
        fields = ['id', 'nom', 'niveau_complexite', 'unites', 'mots_cles']

class ActiviteShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activite
        fields = ['id', 'nom']

class ActiviteFermeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='activite.id')
    nom = serializers.CharField(source='activite.nom', read_only=True)
    mots_cles = serializers.CharField(source='activite.mots_cles', read_only=True)
    niveau_complexite = serializers.IntegerField(source='activite.niveau_complexite', read_only=True)
    unites = UniteSerializer(source='activite.unites', many=True, read_only=True)
    class Meta:
        model = ActiviteFerme
        fields = ['id', 'nom', 'categorie', 'mots_cles', 'niveau_complexite', 'unites']

class UpdateActiviteFermeSerializer(serializers.Serializer):
    activites = serializers.ListField(
        child=serializers.IntegerField()
    )
    categorie = serializers.CharField()

    @transaction.atomic
    def create(self, validated_data):
        ferme = self.context.get('ferme')
        categorie = validated_data.pop('categorie')
        activite_ids = validated_data.pop('activites')
        result = []
        # Cleanup old association
        ActiviteFerme.objects.filter(ferme=ferme, categorie=categorie).delete()

        # Create new association
        for activite_id in activite_ids:
            get_one_or_raise_exception(Activite, CustomException(ErrorCode.ACTIVITE_NOT_FOUND, activite_id), id=activite_id)
            ActiviteFerme.objects.filter(ferme=ferme, activite_id=activite_id).delete() # cleanup old association before
            activite_ferme = ActiviteFerme.objects.create(ferme=ferme, activite_id=activite_id, categorie=categorie)
            result.append(activite_ferme)
        return result