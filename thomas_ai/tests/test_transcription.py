import datetime
import os

from django.core.files.uploadedfile import SimpleUploadedFile

from base.models.vocal import Vocal, VocalStatut
from sebania.utils import transcription_utils
from thomas_ai.tasks.transcription import transcribe
from thomas_ai.tests.TaskTestcase import TaskTestcase



class TestTranscription(TaskTestcase):
    def test_transcription_ok(self):
        user = self.init_current_user()
        expected = ("Bonsoir Charles, "
                           "aujourd'hui j'ai passé trois heures à aider au montage d'une serre chez un collègue, "
                           "une heure à installer du compost sur une planche de carottes, "
                           "20 minutes à arroser les carottes et 30 minutes à faire du rangement de plants. "
                           "Merci, bonne soirée.")
        file_path = os.path.join(self.data_directory, "vocal.m4a")
        with open(file_path, "rb") as f:
            audio_file = SimpleUploadedFile("file_test", f.read(), content_type="audio/mpeg")
        vocal = Vocal.objects.create(user=user, audio=audio_file, date=datetime.datetime.now())
        transcribe.now(vocal_id=vocal.id)
        vocal.refresh_from_db()
        self.compare_transcription(expected, vocal.transcription)
        self.assertEqual(VocalStatut.TRANSCRIBED, vocal.get_statut())
        self.assertIsNotNone(vocal.transcribed_at)
        self.assertIsNotNone(vocal.audio_to_transcription_duration)

    def compare_transcription(self, expected: str, actual: str):
        expected_clean = transcription_utils.cleanup_transcription(expected)
        actual_clean = transcription_utils.cleanup_transcription(actual)
        self.assertEqual(expected_clean, actual_clean)
