from rest_framework import serializers

from base.models import Parcelle, TypeParcelle
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from sebania.utils import db_utils
from sebania.utils.db_utils import get_ferme_from_request


class TypeParcelleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeParcelle
        fields = '__all__'

class ParcelleSerializer(serializers.ModelSerializer):
    type = TypeParcelleSerializer(read_only=True)
    type_id = serializers.IntegerField(write_only=True, allow_null=True)

    class Meta:
        model = Parcelle
        fields = ["id", "nom", "longueur", "largeur", "largeur_planche", "nombre_planches", "type", "type_id"]

    def validate_longueur(self, value):
        if value is not None and value <= 0:
            raise CustomException(ErrorCode.PARCELLE_LONGUEUR_INCORRECT)
        return value

    def validate_largeur(self, value):
        if value is not None and value <= 0:
            raise CustomException(ErrorCode.PARCELLE_LARGEUR_INCORRECT)
        return value

    def validate_nom(self, value):
        request = self.context.get("request")
        ferme = get_ferme_from_request(request)
        parcelles = Parcelle.objects.filter(nom=value, ferme=ferme).all()
        if len(parcelles) > 0:
            raise CustomException(ErrorCode.PARCELLE_NOM_DEJA_EXISTANT, value)
        return value

    def validate_type_id(self, value):
        if value is not None:
            db_utils.get_one_or_raise_exception(TypeParcelle, CustomException(ErrorCode.PARCELLE_NOT_FOUND, value), id=value)
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        ferme = get_ferme_from_request(request)
        return Parcelle.objects.create(ferme=ferme, **validated_data)