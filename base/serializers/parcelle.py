from rest_framework import serializers

from base.models import Parcelle, TypeParcelle


class ParcelleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcelle
        fields = '__all__'

class TypeParcelleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeParcelle
        fields = '__all__'