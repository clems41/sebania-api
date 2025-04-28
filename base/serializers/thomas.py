from rest_framework import serializers

from base.models.vocal import VocalStatut, Vocal

class SendVocalSerializer(serializers.Serializer):
    file = serializers.FileField()

class VocalSerializer(serializers.ModelSerializer):
    statut = serializers.ChoiceField(choices=[tag.name for tag in VocalStatut], read_only=True)

    class Meta:
        model = Vocal
        fields = ["id", "statut"]


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["statut"] = instance.get_statut().value
        return representation