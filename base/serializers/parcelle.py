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
    longueur = serializers.FloatField()
    largeur = serializers.FloatField()
    largeur_planche = serializers.FloatField()
    nombre_planches = serializers.FloatField()
    superficie = serializers.FloatField(read_only=True)
    superficie_cultivee = serializers.FloatField(read_only=True)
    largeur_passe_pieds = serializers.FloatField(read_only=True)

    class Meta:
        model = Parcelle
        fields = ["id", "nom", "longueur", "largeur", "largeur_planche", "nombre_planches", "type", "type_id", "largeur_passe_pieds", "superficie", "superficie_cultivee"]

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
        nb_parcelles_with_same_name = Parcelle.objects.filter(nom=value, ferme=ferme).count()
        if nb_parcelles_with_same_name > 0:
            raise CustomException(ErrorCode.PARCELLE_NOM_DEJA_EXISTANT, value)
        return value

    def validate_type_id(self, value):
        db_utils.get_one_or_raise_exception(TypeParcelle, CustomException(ErrorCode.TYPE_PARCELLE_NOT_FOUND, value), id=value)
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        ferme = get_ferme_from_request(request)
        parcelle = Parcelle.objects.create(ferme=ferme, **validated_data)
        parcelle.fill_empty_fields(all_fields=False)
        return parcelle

    def update(self, instance, validated_data):
        super(ParcelleSerializer, self).update(instance, validated_data)
        instance.fill_empty_fields(all_fields=False)
        return instance



class ParcelleOutputSerializer(serializers.ModelSerializer):
    type = serializers.CharField()

    class Meta:
        model = Parcelle
        fields = ["id", "nom", "longueur", "largeur", "largeur_planche", "nombre_planches", "type", "type_id", "largeur_passe_pieds", "superficie", "superficie_cultivee"]

    def create(self, validated_data):
        ferme = self.context.get("ferme")
        type_nom = validated_data.pop("type")
        type_parcelle = db_utils.get_one_or_raise_exception(TypeParcelle, CustomException(ErrorCode.TYPE_PARCELLE_NOM_NOT_FOUND, type_nom), nom__iexact=type_nom)
        parcelle = Parcelle.objects.create(ferme=ferme, type=type_parcelle, **validated_data)
        parcelle.fill_empty_fields(all_fields=True)
        return parcelle