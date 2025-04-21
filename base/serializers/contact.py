from rest_framework import serializers

from sebania.exceptions.error_code import ErrorCode
from sebania.utils import email_utils


class SendFeedbackSerializer(serializers.Serializer):
    sujet = serializers.CharField()
    message = serializers.CharField(error_messages={"required": ErrorCode.CONTACT_MESSAGE_EMPTY.name})

    def send_feedback(self, sender):
        sujet = self.validated_data.get('sujet')
        message = self.validated_data.get('message')
        email_utils.send_feedback_to_super_users(sender, sujet, message)