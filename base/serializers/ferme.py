from rest_framework import serializers

from base.models import MethodeAgricole


class MethodeAgricoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MethodeAgricole
        fields = '__all__'