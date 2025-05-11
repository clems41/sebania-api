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
        get_one_or_raise_exception(Culture, CustomException(ErrorCode.CULTURE_NOT_FOUND, value), id=value)
        return value

class UpdateCultureFermeSerializer(serializers.Serializer):
    cultures = CultureFermeSerializer(many=True)

    @transaction.atomic
    def create(self, validated_data):
        ferme = self.context.get('ferme')
        result = []
        # Cleanup old association
        CultureFerme.objects.filter(ferme=ferme).delete()

        # Create new association
        for culture in validated_data.pop('cultures'):
            culture_id = culture.pop('culture').pop('id')
            categorie = culture.pop('categorie')
            culture_ferme = CultureFerme.objects.create(ferme=ferme, culture_id=culture_id, categorie=categorie)
            result.append(culture_ferme)
        return result