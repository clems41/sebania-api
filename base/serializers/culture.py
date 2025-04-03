from rest_framework import serializers

from base.models import Unite, Culture, CultureFerme

class UniteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unite
        fields = '__all__'


class CultureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Culture
        fields = ['id', 'nom']

class CultureFermeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='culture.id')
    nom = serializers.CharField(source='culture.nom')
    class Meta:
        model = CultureFerme
        fields = ['id', 'nom', 'categorie']