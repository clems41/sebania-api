import csv
import datetime
import json
import os.path

from base.models.vocal import Vocal, VocalStatut, VocalOrigine
from sebania.tests import test_fixtures
from thomas_ai.tasks.analyze import analyze
from thomas_ai.tests.TaskTestcase import TaskTestcase


class TestAnalyze(TaskTestcase):
    def _analyze_and_get_output(self, user, transcription, origine: VocalOrigine):
        vocal = Vocal.objects.create(user=user, date=datetime.datetime.now(), transcription=transcription, origine=origine)
        analyze.now(vocal_id=vocal.id)
        vocal.refresh_from_db()

        # Check vocal
        self.assertEqual(VocalStatut.ANALYZED, vocal.get_statut())
        self.assertIsNotNone(vocal.analyzed_at)
        self.assertIsNotNone(vocal.transcription_to_output_duration)
        return vocal

    def test_analyze_taches_ok(self):
        user = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=user)
        parcelles = ["Tunnel 1", "Tunnel 2", "Tunnel 3", "Jardin 1", "Jardin 2", "Jardin 3", "Serre 2", "Serre 3"]
        for parcelle in parcelles:
            test_fixtures.create_parcelle(ferme, parcelle)
        transcription = ("bonsoir charles et aujourd'hui j'ai passé trois heures à aider au montage d'une serre chez un "
                           "collègue une heure à installer du compost sur une planche de carottes en tunnel trois 20 minutes à arroser les "
                           "carottes et 30 minutes à faire du rangement de plants merci bonne soirée")
        with open(os.path.join(self.data_directory, "expected_output.json"), "r") as output_file:
            expected_output_data = output_file.read()

        vocal = self._analyze_and_get_output(user, transcription, VocalOrigine.TACHES)

        # Check output
        expected_outputs = json.loads(expected_output_data)
        actual_outputs = vocal.output
        self.assertEqual(len(expected_outputs), len(actual_outputs))
        for expected_output in expected_outputs:
            actual_output = next(
                (output for output in actual_outputs if output["activite"] == expected_output["activite"]),
                None)
            self.assertIsNotNone(actual_output, "L'activite {} n'a pas été trouvé dans la sortie".format(expected_output["activite"]))
            self.assertEqual(expected_output["duree_minutes"], actual_output["duree_minutes"])
            self.assertEqual(expected_output["commentaire"] is None, actual_output["commentaire"] is None)
            for expected_culture in expected_output["cultures"]:
                actual_culture = next(
                    (culture for culture in actual_output["cultures"] if culture["nom"] == expected_culture["nom"]),
                    None)
                self.assertIsNotNone(actual_culture, "La culture {} n'a pas été trouvé dans la sortie".format(expected_culture["nom"]))
                self.assertEqual(expected_culture["unite"], actual_culture["unite"])
                self.assertEqual(expected_culture["quantite"], actual_culture["quantite"])
                self.assertEqual(expected_culture["parcelles"], actual_culture["parcelles"])


    def test_analyze_parcelles_ok(self):
        user = self.init_current_user()
        test_fixtures.create_ferme(responsable=user)
        transcription = ("J'ai 8 tunnels fraise de 4m par 40 j'arrive a y mettre 4 planches généralement des choux parfois les conduit en plein sans planche pour mes oignons par exemple. "
                         "j'ai aussi une parcelle triangulaire de 40m par 50 Enfin c'est plus un trapèze il y a 35 planche de 1m de large la plus grande fait 50 m et la plus petite fait 35m. "
                         "j'ai une pépinière pour faire mes semis avec 4 tables irriguées une des tables est chauffée.")
        with open(os.path.join(self.data_directory, "expected_parcelles.json"), "r") as output_file:
            expected_output_data = output_file.read()

        vocal = self._analyze_and_get_output(user, transcription, VocalOrigine.PARCELLES)

        # Check output
        expected_outputs = json.loads(expected_output_data)
        actual_outputs = vocal.output
        self.assertEqual(len(expected_outputs), len(actual_outputs))
        for expected_output in expected_outputs:
            actual_output = next(
                (output for output in actual_outputs if output["nom"] == expected_output["nom"]),
                None)
            self.assertIsNotNone(actual_output, "La parcelle {} n'a pas été trouvé dans la sortie".format(expected_output["nom"]))
            self.check_response(expected_output, actual_output)
