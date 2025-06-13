from django.db import transaction
from rest_framework import serializers

from base.models import Tache, Parcelle, User, Activite, Culture, Ferme
from base.models.tache import CultureTache
from base.models.unite import Unite
from base.serializers.activite import ActiviteShortSerializer
from base.serializers.culture import CultureSerializer
from base.serializers.unite import UniteSerializer
from base.serializers.user import UserSerializer
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from sebania.utils import db_utils, serializer_utils, ferme_utils
from sebania.utils.db_utils import get_one_or_raise_exception

class TacheParcelleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcelle
        fields = ["id", "nom"]

class CultureTacheSerializer(serializers.ModelSerializer):
    culture = CultureSerializer(read_only=True)
    culture_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    parcelles = TacheParcelleSerializer(read_only=True, many=True)
    parcelle_ids = serializers.ListField(write_only=True, required=False, default=[], allow_empty=True, allow_null=True,
        child=serializers.IntegerField()
    )
    quantite = serializers.FloatField(required=False, allow_null=True)
    nature = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    unite_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    unite = UniteSerializer(read_only=True)
    fields_are_missing = serializers.BooleanField(read_only=True)

    class Meta:
        model = CultureTache
        fields = ["culture", "culture_id", "parcelles", "parcelle_ids", "quantite", "nature", "unite", "unite_id", "fields_are_missing"]

    def validate_culture_id(self, value):
        if value is not None:
            db_utils.get_one_or_raise_exception(Culture, CustomException(ErrorCode.CULTURE_NOT_FOUND, value), id=value)
        return value

    def validate_unite_id(self, value):
        if value is not None:
            db_utils.get_one_or_raise_exception(Unite, CustomException(ErrorCode.UNITE_NOT_FOUND, value), id=value)
        return value

    def validate_parcelle_ids(self, value):
        if value is not None:
            for parcelle_id in value:
                db_utils.get_one_or_raise_exception(Parcelle, CustomException(ErrorCode.PARCELLE_NOT_FOUND, parcelle_id), id=parcelle_id)
        return value

    def create(self, validated_data):
        ferme = serializer_utils.get_ferme_from_context(self.context)
        parcelle_ids = validated_data.pop('parcelle_ids')
        instance = super(CultureTacheSerializer, self).create(validated_data)
        if parcelle_ids is not None:
            for parcelle_id in parcelle_ids:
                parcelle = db_utils.get_one_or_raise_exception(Parcelle,
                                                               CustomException(ErrorCode.PARCELLE_NOT_FOUND, parcelle_id),
                                                               id=parcelle_id, ferme=ferme)
                instance.parcelles.add(parcelle)
        return instance


class TacheSerializer(serializers.ModelSerializer):
    activite = ActiviteShortSerializer(read_only=True)
    activite_id = serializers.IntegerField(write_only=True)
    date = serializers.DateField(input_formats=['%d/%m/%Y'], format='%d/%m/%Y')
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    duree_minutes = serializers.IntegerField()
    cultures = CultureTacheSerializer(many=True)
    commentaire = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    vocal_id = serializers.IntegerField(read_only=True)
    fields_are_missing = serializers.BooleanField(read_only=True)
    parcelles = TacheParcelleSerializer(read_only=True, many=True)
    parcelle_ids = serializers.ListField(write_only=True, required=False, default=[], allow_empty=True, allow_null=True,
        child=serializers.IntegerField()
    )
    quantite = serializers.FloatField(required=False, allow_null=True)
    nature = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    unite_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    unite = UniteSerializer(read_only=True)

    class Meta:
        model = Tache
        fields = ["id", "activite", "activite_id", "date", "user", "user_id", "duree_minutes", "cultures", "commentaire", "fields_are_missing", "vocal_id", "parcelles", "parcelle_ids", "quantite", "nature", "unite", "unite_id"]

    def to_representation(self, instance: Tache):
        representation = super().to_representation(instance)
        representation["fields_are_missing"] = instance.get_fields_are_missing()
        for culture_tache_idx, culture_tache in enumerate(representation["cultures"]):
            culture_tache["fields_are_missing"] = instance.cultures.all()[culture_tache_idx].get_fields_are_missing(instance.activite.niveau_complexite)
        return representation

    def validate_activite_id(self, value):
        db_utils.get_one_or_raise_exception(Activite, CustomException(ErrorCode.ACTIVITE_NOT_FOUND, value), id=value)
        return value

    def validate_user_id(self, value):
        ferme = serializer_utils.get_ferme_from_context(self.context)
        user = db_utils.get_one_or_raise_exception(User, CustomException(ErrorCode.USER_NOT_FOUND, value), id=value)
        if not ferme_utils.user_is_in_ferme(user, ferme):
            raise CustomException(ErrorCode.USER_NOT_FOUND, value)
        user_who_sent_request = self.context.get("request").user
        if db_utils.user_is_employe(user_who_sent_request.id):
            if user_who_sent_request.id != user.id:
                raise CustomException(ErrorCode.USER_EMPLOYE_CANNOT_POST_FOR_RESPONSABLE)
        return value

    def validate_duree_minutes(self, value):
        if value < 1 or value >= 60*24:
            raise CustomException(ErrorCode.TACHE_DUREE_INCORRECTE, value)
        return value

    def _add_cultures(self, cultures, instance: Tache, ferme: Ferme):
        # Create new ones
        if cultures is not None:
            # Cleanup old cultures
            instance.cultures.all().delete()
            for culture in cultures:
                serializer = CultureTacheSerializer(data=culture, context={"ferme": ferme})
                serializer.is_valid(raise_exception=True)
                culture_tache = serializer.save()
                instance.cultures.add(culture_tache)

    def _add_parcelles(self, parcelle_ids, instance: Tache, ferme: Ferme):
        # Create new ones
        if parcelle_ids is not None:
            # Cleanup old parcelles
            instance.parcelles.clear()
            for parcelle_id in parcelle_ids:
                parcelle = get_one_or_raise_exception(Parcelle, CustomException(ErrorCode.PARCELLE_NOT_FOUND, parcelle_id), id=parcelle_id, ferme=ferme)
                instance.parcelles.add(parcelle)

    @transaction.atomic
    def _create_or_update(self, instance, validated_data):
        ferme = serializer_utils.get_ferme_from_context(self.context)
        cultures = validated_data.pop("cultures", None)
        parcelle_ids = validated_data.pop("parcelle_ids", None)
        validated_data["ferme_id"] = ferme.id
        if instance is None:
            instance = super(TacheSerializer, self).create(validated_data)
        else:
            instance = super(TacheSerializer, self).update(instance, validated_data)
        self._add_cultures(cultures, instance, ferme)
        self._add_parcelles(parcelle_ids, instance, ferme)
        return instance


    def create(self, validated_data):
        return self._create_or_update(None, validated_data)

    def update(self, instance, validated_data):
        return self._create_or_update(instance, validated_data)