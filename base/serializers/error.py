from rest_framework import serializers


class ErrorSerializer(serializers.Serializer):
    code = serializers.CharField()