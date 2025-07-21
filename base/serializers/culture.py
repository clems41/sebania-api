from django.db import transaction
from rest_framework import serializers

from base.models import Culture, CultureFerme
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from sebania.utils.db_utils import get_one_or_raise_exception


class CultureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Culture
        fields = ['id', 'nom']

class CultureFermeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='culture.id')
    nom = serializers.CharField(source='culture.nom', read_only=True)
    class Meta:
        model = CultureFerme
        fields = ['id', 'nom', 'categorie']

    def validate_id(self, value):
        return value

class UpdateCultureFermeSerializer(serializers.Serializer):
    cultures = serializers.ListField(
        child=serializers.IntegerField()
    )
    categorie = serializers.CharField()

    @transaction.atomic
    def create(self, validated_data):
        ferme = self.context.get('ferme')
        categorie = validated_data.pop('categorie')
        culture_ids = validated_data.pop('cultures')
        result = []
        # Cleanup old association
        CultureFerme.objects.filter(ferme=ferme, categorie=categorie).delete()

        # Create new association
        for culture_id in culture_ids:
            get_one_or_raise_exception(Culture, CustomException(ErrorCode.CULTURE_NOT_FOUND, culture_id), id=culture_id)
            CultureFerme.objects.filter(ferme=ferme, culture_id=culture_id).delete() # cleanup old association before
            culture_ferme = CultureFerme.objects.create(ferme=ferme, culture_id=culture_id, categorie=categorie)
            result.append(culture_ferme)
        return result