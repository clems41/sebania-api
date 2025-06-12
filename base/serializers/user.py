from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from base.models import User


class UserSerializer(ModelSerializer):
    roles = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', "roles")
        extra_kwargs = {'password': {'write_only': True}}

    def to_representation(self, instance):
        representation = super(UserSerializer, self).to_representation(instance)
        representation["roles"] = ','.join([group.name for group in instance.groups.all()])
        return representation

    def create(self, validated_data, **kwargs):
        return User.objects.create_user(**validated_data)