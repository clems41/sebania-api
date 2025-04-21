from typing import List

from django.db import transaction
from rest_framework import serializers

from base.models import Tache, Parcelle, User, Activite, Culture, Ferme
from base.models.statut import StatutTache
from base.serializers.activite import ActiviteSerializer
from base.serializers.culture import CultureSerializer
from base.serializers.parcelle import ParcelleSerializer
from base.serializers.user import UserSerializer
from sebania.exceptions.activite import ActiviteNotFoundException
from sebania.exceptions.auth import EmployeCannotActForResponsableException
from sebania.exceptions.culture import CultureNotFoundException
from sebania.exceptions.parcelle import ParcelleNotFoundException
from sebania.exceptions.tache import TacheDureeIncorrecteException
from sebania.exceptions.user import UserNotFoundException
from sebania.utils import db_utils, serializer_utils, ferme_utils


class TacheSerializer(serializers.ModelSerializer):
    activite = ActiviteSerializer(read_only=True)
    activite_id = serializers.IntegerField(write_only=True)
    date = serializers.DateField(input_formats=['%d/%m/%Y'], format='%d/%m/%Y')
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    duree_minutes = serializers.IntegerField()
    culture = CultureSerializer(read_only=True)
    culture_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    parcelles = ParcelleSerializer(read_only=True, many=True)
    parcelle_ids = serializers.ListField(write_only=True, required=False, default=[], allow_empty=True, allow_null=True,
        child=serializers.IntegerField()
    )
    quantite_recoltee = serializers.IntegerField(required=False, allow_null=True)
    commentaire = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    quantite = serializers.FloatField(required=False, allow_null=True)
    nature = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    unite = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    statut = serializers.CharField(read_only=True)

    class Meta:
        model = Tache
        fields = ["id", "activite", "activite_id", "date", "user", "user_id", "duree_minutes", "culture", "culture_id",
                  "parcelles", "parcelle_ids", "quantite_recoltee", "commentaire", "quantite", "nature", "unite",
                  "statut"]

    def to_representation(self, instance: Tache):
        representation = super().to_representation(instance)
        representation["statut"] = instance.get_statut().name
        return representation

    def validate_activite_id(self, value):
        db_utils.get_one_or_raise_exception(Activite, ActiviteNotFoundException(value), id=value)
        return value

    def validate_culture_id(self, value):
        if value is not None:
            db_utils.get_one_or_raise_exception(Culture, CultureNotFoundException(value), id=value)
        return value

    def validate_user_id(self, value):
        ferme = serializer_utils.get_ferme_from_context(self.context)
        user = db_utils.get_one_or_raise_exception(User, UserNotFoundException(value), id=value)
        if not ferme_utils.user_is_in_ferme(user, ferme):
            raise UserNotFoundException(value)
        user_who_sent_request = self.context.get("request").user
        if db_utils.user_is_employe(user_who_sent_request.id):
            if user_who_sent_request.id != user.id:
                raise EmployeCannotActForResponsableException()
        return value

    def validate_duree_minutes(self, value):
        if value < 1 or value >= 60*24:
            raise TacheDureeIncorrecteException()
        return value

    def _add_parcelles(self, parcelle_ids: List[int], instance: Tache, ferme: Ferme):
        if parcelle_ids is not None:
            for parcelle_id in parcelle_ids:
                # Check that parcelle exists in database
                db_utils.get_one_or_raise_exception(Parcelle, ParcelleNotFoundException(parcelle_id, ferme.id), id=parcelle_id)
            instance.parcelles.set(parcelle_ids)

    @transaction.atomic
    def _create_or_update(self, instance, validated_data):
        ferme = serializer_utils.get_ferme_from_context(self.context)
        parcelle_ids = validated_data.pop("parcelle_ids")
        validated_data["ferme_id"] = ferme.id
        if instance is None:
            instance = super(TacheSerializer, self).create(validated_data)
        else:
            instance = super(TacheSerializer, self).update(instance, validated_data)
        self._add_parcelles(parcelle_ids, instance, ferme)
        return instance


    def create(self, validated_data):
        return self._create_or_update(None, validated_data)

    def update(self, instance, validated_data):
        return self._create_or_update(instance, validated_data)


class CalendrierJourSerializer(serializers.Serializer):
    jour = serializers.DateField(format="%d/%m/%Y", input_formats=['%d/%m/%Y'])
    total_jour = serializers.IntegerField()
    statut = serializers.ChoiceField(choices=[tag.name for tag in StatutTache])


class CalendrierSerializer(serializers.Serializer):
    jours = CalendrierJourSerializer(many=True)
    total = serializers.IntegerField()
    statut = serializers.ChoiceField(choices=[tag.name for tag in StatutTache])