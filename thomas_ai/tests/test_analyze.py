import csv
import datetime
import json
import os.path

from base.models.vocal import Vocal, VocalStatut
from thomas_ai.tasks.analyze import analyze
from thomas_ai.tests.TaskTestcase import TaskTestcase


class TestAnalyze(TaskTestcase):
    def test_analyze_ok(self):
        user = self.init_current_user()
        transcription = ("bonsoir charles et aujourd'hui j'ai passé trois heures à aider au montage d'une serre chez un "
                           "collègue une heure à installer du compost sur une planche de carottes 20 minutes à arroser les "
                           "carottes et 30 minutes à faire du rangement de plants merci bonne soirée")
        with open(os.path.join(self.data_directory, "expected_output.json"), "r") as output_file:
            expected_output_data = output_file.read()
        vocal = Vocal.objects.create(user=user, date=datetime.datetime.now(), transcription=transcription)
        analyze.now(vocal_id=vocal.id)
        vocal.refresh_from_db()

        # Check vocal
        self.assertEqual(VocalStatut.ANALYZED, vocal.get_statut())
        self.assertIsNotNone(vocal.analyzed_at)
        self.assertIsNotNone(vocal.transcription_to_output_duration)

        # Check output
        expected_outputs = json.loads(expected_output_data)
        actual_outputs = vocal.output
        self.assertEqual(len(expected_outputs), len(actual_outputs))
        for expected_output in expected_outputs:
            actual_output = next(
                (output for output in actual_outputs if output["activite"] == expected_output["activite"]),
                None)
            self.assertIsNotNone(actual_output, "L'activite {} n'a pas été trouvé dans la sortie".format(expected_output["activite"]))
            self.assertEqual(expected_output["cultures"], actual_output["cultures"])
            self.assertEqual(expected_output["duree_minutes"], actual_output["duree_minutes"])
            self.assertEqual(expected_output["quantite"], actual_output["quantite"])
            self.assertEqual(expected_output["unite"], actual_output["unite"])
            self.assertEqual(expected_output["commentaire"] is None, actual_output["commentaire"] is None)
