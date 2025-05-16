from rest_framework import serializers

from base.models import Tache, Activite, Culture, Parcelle, Unite
from base.models.tache import CultureTache
from base.models.vocal import Vocal
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from sebania.utils.db_utils import get_ferme_for_user, get_one_or_none, get_one_or_raise_exception


class CultureTacheOutputSerializer(serializers.ModelSerializer):
    nom = serializers.CharField()
    parcelles = serializers.ListField(required=False, default=[], allow_empty=True, allow_null=True,
                                      child=serializers.CharField()
                                      )
    unite = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = CultureTache
        fields = ["parcelles", "nom", "unite", "quantite", "nature"]

    def create(self, validated_data):
        ferme = self.context.get("ferme")
        culture_nom = validated_data.get("nom", None)
        culture = get_one_or_none(Culture, nom__iexact=culture_nom)
        unite_nom = validated_data.get("unite", None)
        unite = get_one_or_none(Unite, nom__iexact=unite_nom)
        quantite = validated_data.get("quantite", None)
        nature = validated_data.get("nature", None)
        if culture is not None:
            instance = CultureTache.objects.create(culture=culture, quantite=quantite, unite=unite, nature=nature)
            # Ajout des parcelles
            parcelles = validated_data.get("parcelles")
            if parcelles is not None:
                for parcelle_nom in parcelles:
                    parcelle = get_one_or_none(Parcelle, nom__iexact=parcelle_nom, ferme=ferme)
                    if parcelle is not None:
                        instance.parcelles.add(parcelle)
            return instance
        return None


class TacheOutputSerializer(serializers.ModelSerializer):
    cultures = CultureTacheOutputSerializer(many=True)
    activite = serializers.CharField()

    class Meta:
        model = Tache
        fields = ["duree_minutes", "commentaire", "vocal_id", "activite", "cultures"]

    def validate_activite(self, activite):
        get_one_or_raise_exception(Activite, CustomException(ErrorCode.ACTIVITE_NOM_NOT_FOUND, activite),
                                   nom__iexact=activite)
        return activite

    def create(self, validated_data, **kwargs):
        vocal_id = self.context.get("vocal_id")
        activite_nom = validated_data.pop("activite")
        cultures = validated_data.pop("cultures")
        vocal = Vocal.objects.get(id=vocal_id)
        user = vocal.user
        ferme = get_ferme_for_user(user.id)
        date = vocal.date
        activite = Activite.objects.get(nom__iexact=activite_nom)

        # Creation de la tâche
        tache = Tache.objects.create(**validated_data, date=date, user=user, activite=activite, ferme=ferme, vocal_id=vocal_id)

        # Ajout des cultures
        if cultures is not None:
            for culture in cultures:
                serializer = CultureTacheOutputSerializer(data=culture, context={"ferme": ferme})
                serializer.is_valid(raise_exception=True)
                culture_tache = serializer.save()
                tache.cultures.add(culture_tache)
        return tache
