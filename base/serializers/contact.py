from rest_framework import serializers

from sebania.utils import email_utils


class SendFeedbackSerializer(serializers.Serializer):
    sujet = serializers.CharField()
    message = serializers.CharField()

    def send_feedback(self, sender):
        sujet = self.validated_data.get('sujet')
        message = self.validated_data.get('message')
        email_utils.send_feedback_to_super_users(sender, sujet, message)