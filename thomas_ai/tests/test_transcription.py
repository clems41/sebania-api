import datetime
import os.path

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from base.models.vocal import Vocal, VocalStatut
from sebania.tests.SebaniaTestCase import SebaniaTestCase
from thomas_ai.tasks.transcription import transcribe


class TestTranscription(SebaniaTestCase):
    def test_transcription_ok(self):
        user = self.init_current_user()
        expected_result = ("bonsoir charles et aujourd'hui j'ai passé trois heures à aider au montage d'une serre chez un "
                           "collègue une heure à installer du compost sur une planche de carottes 20 minutes à arroser les "
                           "carottes et 30 minutes à faire du rangement de plants merci bonne soirée")
        file_path = os.path.join(settings.FIXTURE_DIRS[0].as_posix(), "../../thomas_ai/tests/data/vocal.mp3")
        with open(file_path, "rb") as f:
            audio_file = SimpleUploadedFile("file_test", f.read(), content_type="audio/mpeg")
        vocal = Vocal.objects.create(user=user, audio=audio_file, date=datetime.datetime.now())
        transcribe.now(vocal_id=vocal.id)
        vocal.refresh_from_db()
        self.assertEqual(expected_result.strip(), vocal.transcription.strip())
        self.assertEqual(VocalStatut.TRANSCRIBED, vocal.get_statut())
        self.assertIsNotNone(vocal.transcribed_at)
        self.assertIsNotNone(vocal.audio_to_transcription_duration)
