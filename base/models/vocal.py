import datetime
from enum import Enum

from base.models import User
from base.models.base import BaseModel
from django.db import models

class VocalStatut(Enum):
    RECEIVED = "received"
    TRANSCRIBED = "transcribed"
    FINISHED = "finished"

def get_upload_path(instance, filename):
    if filename == "file":
        filename = get_audio_name(instance)
    return "vocaux/{}/{}/{}".format(instance.user.id, instance.date.strftime("%d%m%Y"), filename)

def get_audio_name(instance):
    existing_vocaux_for_user_and_date = Vocal.objects.filter(user=instance.user, date=instance.date).all()
    return "{}.mp3".format(len(existing_vocaux_for_user_and_date) + 1)

class Vocal(BaseModel):
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    audio = models.FileField(upload_to=get_upload_path)
    transcription = models.TextField(blank=True, null=True)
    output = models.JSONField(blank=True, null=True)
    audio_to_transcription_duration = models.DurationField(blank=True, null=True)
    transcription_to_output_duration = models.DurationField(blank=True, null=True)

    def get_statut(self):
        statut = VocalStatut.RECEIVED
        if self.transcription:
            statut = VocalStatut.TRANSCRIBED
        if self.output:
            statut = VocalStatut.FINISHED
        return statut