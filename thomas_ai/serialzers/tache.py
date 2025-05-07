from rest_framework import serializers

from base.models import Tache, Activite, Culture, Parcelle, Unite
from base.models.vocal import Vocal
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
from sebania.utils.db_utils import get_ferme_for_user, get_one_or_none, get_one_or_raise_exception


class TacheOutputSerializer(serializers.ModelSerializer):
    cultures = serializers.ListField(required=False, default=[], allow_empty=True, allow_null=True,
        child=serializers.CharField()
    )
    parcelles = serializers.ListField(required=False, default=[], allow_empty=True, allow_null=True,
        child=serializers.CharField()
    )
    activite = serializers.CharField()
    unite = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    class Meta:
        model = Tache
        fields = ["duree_minutes", "commentaire", "quantite", "unite", "nature", "vocal_id", "activite", "cultures", "parcelles"]

    def validate_activite(self, activite):
        get_one_or_raise_exception(Activite, CustomException(ErrorCode.ACTIVITE_NOM_NOT_FOUND, activite), nom__iexact=activite)
        return activite

    def create(self, validated_data, **kwargs):
        vocal_id = self.context.get("vocal_id")
        unite_nom = validated_data.pop("unite")
        activite_nom = validated_data.pop("activite")
        culture_noms = validated_data.pop("cultures")
        parcelle_noms = validated_data.pop("parcelles")
        vocal = Vocal.objects.get(id=vocal_id)
        user = vocal.user
        ferme = get_ferme_for_user(user)
        date = vocal.date
        activite = Activite.objects.get(nom__iexact=activite_nom)

        # Récupération de l'unité
        unite = None
        if unite_nom:
            unite = get_one_or_none(Unite, nom__iexact=unite_nom)

        # Creation de la tâche
        tache = Tache.objects.create(**validated_data, date=date, user=user, activite=activite, unite=unite,
                                     ferme=ferme, vocal_id=vocal_id)

        # Ajout des cultures
        for culture_nom in culture_noms:
            culture = get_one_or_none(Culture, nom__iexact=culture_nom)
            if culture is not None:
                tache.cultures.add(culture)

        # Ajout des parcelles
        for parcelle_nom in parcelle_noms:
            parcelle = get_one_or_none(Parcelle, nom__iexact=parcelle_nom, ferme=ferme)
            if parcelle is not None:
                tache.parcelles.add(parcelle)
        return tache