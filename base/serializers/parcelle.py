from rest_framework import serializers

from base.models import Parcelle, TypeParcelle, Ferme
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

    def validate_type_id(self, value):
        db_utils.get_one_or_raise_exception(TypeParcelle, CustomException(ErrorCode.TYPE_PARCELLE_NOT_FOUND, value), id=value)
        return value

    def check_if_nom_already_exists(self, nom: str, ferme: Ferme, existing_parcelle_id: int = None):
        existing_parcelle_ids = []
        if existing_parcelle_id is not None:
            existing_parcelle_ids.append(existing_parcelle_id)
        nb_parcelles_with_same_name = Parcelle.objects.filter(nom=nom, ferme=ferme).exclude(id__in=existing_parcelle_ids).count()
        if nb_parcelles_with_same_name > 0:
            raise CustomException(ErrorCode.PARCELLE_NOM_DEJA_EXISTANT, nom)

    def create(self, validated_data):
        request = self.context.get("request")
        ferme = get_ferme_from_request(request)
        self.check_if_nom_already_exists(validated_data["nom"], ferme)
        parcelle = Parcelle.objects.create(ferme=ferme, **validated_data)
        parcelle.fill_empty_fields(all_fields=False)
        return parcelle

    def update(self, instance, validated_data):
        request = self.context.get("request")
        ferme = get_ferme_from_request(request)
        self.check_if_nom_already_exists(validated_data["nom"], ferme, instance.id)
        super(ParcelleSerializer, self).update(instance, validated_data)
        instance.fill_empty_fields(all_fields=False)
        return instance



class ParcelleOutputSerializer(serializers.ModelSerializer):
    type = serializers.CharField(allow_blank=True)

    class Meta:
        model = Parcelle
        fields = ["id", "nom", "longueur", "largeur", "largeur_planche", "nombre_planches", "type", "type_id", "largeur_passe_pieds", "superficie", "superficie_cultivee"]

    def create(self, validated_data):
        ferme = self.context.get("ferme")
        type_nom = validated_data.pop("type")
        if type_nom is None:
            type_parcelle = db_utils.get_one_or_raise_exception(TypeParcelle, CustomException(ErrorCode.TYPE_PARCELLE_NOM_NOT_FOUND, type_nom), nom__iexact=type_nom)
        else:
            type_parcelle = TypeParcelle.objects.get(id=1)
        parcelle = Parcelle.objects.create(ferme=ferme, type=type_parcelle, **validated_data)
        parcelle.fill_empty_fields(all_fields=True)
        return parcelle