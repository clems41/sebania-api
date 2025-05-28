from rest_framework import serializers

from base.models import Parcelle, TypeParcelle
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from sebania.utils import db_utils
from sebania.utils.db_utils import get_ferme_from_request
from sebania.utils.serializer_utils import is_not_zero


class TypeParcelleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeParcelle
        fields = '__all__'

class ParcelleSerializer(serializers.ModelSerializer):
    type = TypeParcelleSerializer(read_only=True)
    type_id = serializers.IntegerField(write_only=True, allow_null=True)

    class Meta:
        model = Parcelle
        fields = ["id", "nom", "longueur", "largeur", "largeur_planche", "nombre_planches", "type", "type_id", "largeur_passe_pieds", "superficie"]

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
        if value is not None:
            db_utils.get_one_or_raise_exception(TypeParcelle, CustomException(ErrorCode.TYPE_PARCELLE_NOT_FOUND, value), id=value)
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        ferme = get_ferme_from_request(request)
        return Parcelle.objects.create(ferme=ferme, **validated_data)


class ParcelleOutputSerializer(serializers.ModelSerializer):
    type = serializers.CharField()

    class Meta:
        model = Parcelle
        fields = ["id", "nom", "longueur", "largeur", "largeur_planche", "nombre_planches", "type", "type_id", "largeur_passe_pieds", "superficie", "superficie_cultivee"]

    def get_longueur(self, validated_data):
        longueur = validated_data.get("longueur")
        largeur = validated_data.get("largeur")
        superficie = validated_data.get("superficie")
        if is_not_zero(longueur):
            return longueur
        else:
            if is_not_zero(largeur) and is_not_zero(superficie):
                return superficie / largeur
        return 0

    def get_largeur(self, validated_data):
        longueur = validated_data.get("longueur")
        largeur = validated_data.get("largeur")
        largeur_planche = validated_data.get("largeur_planche")
        nombre_planches = validated_data.get("nombre_planches")
        largeur_passe_pieds = validated_data.get("largeur_passe_pieds")
        superficie = validated_data.get("superficie")
        if is_not_zero(largeur):
            return largeur
        else:
            if is_not_zero(longueur) and is_not_zero(superficie):
                return round(superficie / longueur, 3)
            if is_not_zero(largeur_planche) and is_not_zero(largeur_passe_pieds) and is_not_zero(nombre_planches):
                return (largeur_planche + largeur_passe_pieds) * nombre_planches
        return 0

    def get_largeur_planche(self, validated_data):
        largeur = validated_data.get("largeur")
        largeur_planche = validated_data.get("largeur_planche")
        nombre_planches = validated_data.get("nombre_planches")
        largeur_passe_pieds = validated_data.get("largeur_passe_pieds")
        if is_not_zero(largeur_planche):
            return largeur_planche
        else:
            if is_not_zero(largeur) and is_not_zero(largeur_passe_pieds) and is_not_zero(nombre_planches):
                return round((largeur / nombre_planches) - largeur_passe_pieds, 3)
        return 0

    def get_nombre_planches(self, validated_data):
        largeur = validated_data.get("largeur")
        largeur_planche = validated_data.get("largeur_planche")
        nombre_planches = validated_data.get("nombre_planches")
        largeur_passe_pieds = validated_data.get("largeur_passe_pieds")
        if is_not_zero(nombre_planches):
            return nombre_planches
        else:
            if is_not_zero(largeur_planche) and is_not_zero(largeur) and is_not_zero(largeur_passe_pieds):
                return round(largeur / (largeur_planche + largeur_passe_pieds), 3)
        return 0

    def get_largeur_passe_pieds(self, validated_data):
        largeur = validated_data.get("largeur")
        largeur_planche = validated_data.get("largeur_planche")
        nombre_planches = validated_data.get("nombre_planches")
        largeur_passe_pieds = validated_data.get("largeur_passe_pieds")
        if is_not_zero(largeur_passe_pieds):
            return largeur_passe_pieds
        else:
            if is_not_zero(largeur_planche) and is_not_zero(largeur) and is_not_zero(nombre_planches):
                return round((largeur / nombre_planches) - largeur_planche, 3)
        return 0

    def get_superficie(self, validated_data):
        superficie = validated_data.get("superficie")
        if is_not_zero(superficie):
            return superficie
        else:
            longueur = self.get_longueur(validated_data)
            largeur = self.get_largeur(validated_data)
            if is_not_zero(longueur) and is_not_zero(largeur):
                return longueur * largeur
        return 0

    def get_superficie_cultivee(self, validated_data):
        longueur = self.get_longueur(validated_data)
        largeur_planche = self.get_largeur_planche(validated_data)
        nombre_planches = self.get_nombre_planches(validated_data)
        if is_not_zero(longueur) and is_not_zero(largeur_planche) and is_not_zero(nombre_planches):
            return longueur * largeur_planche * nombre_planches
        return 0


    def create(self, validated_data):
        ferme = self.context.get("ferme")
        type_nom = validated_data.pop("type")
        nom = validated_data.pop("nom")
        type_parcelle = db_utils.get_one_or_raise_exception(TypeParcelle, CustomException(ErrorCode.TYPE_PARCELLE_NOM_NOT_FOUND, type_nom), nom__iexact=type_nom)
        return Parcelle.objects.create(ferme=ferme, type=type_parcelle,
                                       longueur=self.get_longueur(validated_data),
                                       largeur=self.get_largeur(validated_data),
                                       largeur_planche=self.get_largeur_planche(validated_data),
                                       nombre_planches=self.get_nombre_planches(validated_data),
                                       largeur_passe_pieds=self.get_largeur_passe_pieds(validated_data),
                                       superficie=self.get_superficie(validated_data),
                                       superficie_cultivee=self.get_superficie_cultivee(validated_data),
                                       nom=nom)