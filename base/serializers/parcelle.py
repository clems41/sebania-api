from rest_framework import serializers

from base.models import Parcelle, TypeParcelle
from sebania.exceptions.parcelle import ParcelleTypeNotFoundException, ParcelleSuperficieNulleException, \
    ParcelleNomDejaExistantException
from sebania.utils import db_utils
from sebania.utils.db_utils import get_ferme_for_user


class TypeParcelleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeParcelle
        fields = '__all__'

class ParcelleSerializer(serializers.ModelSerializer):
    type = TypeParcelleSerializer(read_only=True)
    type_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Parcelle
        fields = ["id", "nom", "superficie", "type", "type_id"]

    def validate_superficie(self, value):
        if value <= 0:
            raise ParcelleSuperficieNulleException()
        return value

    def validate_nom(self, value):
        request = self.context.get("request")
        ferme = get_ferme_for_user(request)
        parcelles = Parcelle.objects.filter(nom=value, ferme=ferme).all()
        if len(parcelles) > 0:
            raise ParcelleNomDejaExistantException(value)
        return value

    def validate_type_id(self, value):
        db_utils.get_one_or_raise_exception(TypeParcelle, ParcelleTypeNotFoundException(value), id=value)
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        ferme = get_ferme_for_user(request)
        return Parcelle.objects.create(ferme=ferme, **validated_data)