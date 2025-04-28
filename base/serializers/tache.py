from typing import List

from django.db import transaction
from rest_framework import serializers

from base.models import Tache, Parcelle, User, Activite, Culture, Ferme
from base.serializers.activite import ActiviteSerializer
from base.serializers.culture import CultureSerializer
from base.serializers.parcelle import ParcelleSerializer
from base.serializers.unite import UniteSerializer
from base.serializers.user import UserSerializer
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from sebania.utils import db_utils, serializer_utils, ferme_utils


class TacheSerializer(serializers.ModelSerializer):
    activite = ActiviteSerializer(read_only=True)
    activite_id = serializers.IntegerField(write_only=True)
    date = serializers.DateField(input_formats=['%d/%m/%Y'], format='%d/%m/%Y')
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    duree_minutes = serializers.IntegerField()
    cultures = CultureSerializer(read_only=True, many=True)
    culture_ids = serializers.ListField(write_only=True, required=False, default=[], allow_empty=True, allow_null=True,
        child=serializers.IntegerField()
    )
    parcelles = ParcelleSerializer(read_only=True, many=True)
    parcelle_ids = serializers.ListField(write_only=True, required=False, default=[], allow_empty=True, allow_null=True,
        child=serializers.IntegerField()
    )
    commentaire = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    quantite = serializers.FloatField(required=False, allow_null=True)
    nature = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    unite_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    unite = UniteSerializer(read_only=True)
    fields_are_missing = serializers.BooleanField(read_only=True)

    class Meta:
        model = Tache
        fields = ["id", "activite", "activite_id", "date", "user", "user_id", "duree_minutes", "cultures", "culture_ids",
                  "parcelles", "parcelle_ids", "commentaire", "quantite", "nature", "unite", "unite_id", "fields_are_missing"]

    def to_representation(self, instance: Tache):
        representation = super().to_representation(instance)
        representation["fields_are_missing"] = instance.get_fields_are_missing()
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
                raise CustomException(ErrorCode.AUTH_EMPLOYE_CANNOT_POST_FOR_RESPONSABLE)
        return value

    def validate_duree_minutes(self, value):
        if value < 1 or value >= 60*24:
            raise CustomException(ErrorCode.TACHE_DUREE_INCORRECTE, value)
        return value

    def _add_parcelles(self, parcelle_ids: List[int], instance: Tache, ferme: Ferme):
        if parcelle_ids is not None:
            for parcelle_id in parcelle_ids:
                # Check that parcelle exists in database
                db_utils.get_one_or_raise_exception(Parcelle, CustomException(ErrorCode.PARCELLE_NOT_FOUND, parcelle_id), id=parcelle_id)
            instance.parcelles.set(parcelle_ids)

    def _add_cultures(self, culture_ids: List[int], instance: Tache):
        if culture_ids is not None:
            for culture_id in culture_ids:
                # Check that parcelle exists in database
                db_utils.get_one_or_raise_exception(Culture, CustomException(ErrorCode.CULTURE_NOT_FOUND, culture_id), id=culture_id)
            instance.cultures.set(culture_ids)

    @transaction.atomic
    def _create_or_update(self, instance, validated_data):
        ferme = serializer_utils.get_ferme_from_context(self.context)
        parcelle_ids = validated_data.pop("parcelle_ids")
        culture_ids = validated_data.pop("culture_ids")
        validated_data["ferme_id"] = ferme.id
        if instance is None:
            instance = super(TacheSerializer, self).create(validated_data)
        else:
            instance = super(TacheSerializer, self).update(instance, validated_data)
        self._add_parcelles(parcelle_ids, instance, ferme)
        self._add_cultures(culture_ids, instance)
        return instance


    def create(self, validated_data):
        return self._create_or_update(None, validated_data)

    def update(self, instance, validated_data):
        return self._create_or_update(instance, validated_data)