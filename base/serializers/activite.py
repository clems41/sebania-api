from rest_framework import serializers

from base.models import Activite, ActiviteFerme


class ActiviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activite
        fields = ['id', 'nom']

class ActiviteFermeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='activite.id')
    nom = serializers.CharField(source='activite.nom')
    class Meta:
        model = ActiviteFerme
        fields = ['id', 'nom', 'categorie']