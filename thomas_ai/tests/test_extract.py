import datetime
import json
import os.path

from base.models import Tache
from base.models.vocal import Vocal, VocalStatut
from sebania.tests import test_fixtures
from thomas_ai.tasks.extract import extract
from thomas_ai.tests.TaskTestcase import TaskTestcase


class TestExtract(TaskTestcase):
    def test_extract_ok(self):
        user = self.init_current_user()
        test_fixtures.create_ferme(user)
        with open(os.path.join(self.data_directory, "expected_output.json"), "r") as output_file:
            output_data = json.loads(output_file.read())
        vocal = Vocal.objects.create(user=user, date=datetime.datetime.now(), output=output_data)
        extract.now(vocal_id=vocal.id)
        vocal.refresh_from_db()

        # Check vocal
        self.assertEqual(VocalStatut.FINISHED, vocal.get_statut())
        self.assertIsNotNone(vocal.finished_at)

        # Check taches
        taches = Tache.objects.filter(vocal_id=vocal.id)
        self.assertEqual(len(taches), len(output_data))
        for expected_tache in output_data:
            actual_tache = next(tache for tache in taches if tache.activite.nom == expected_tache["activite"])
            self.assertIsNotNone(actual_tache)
            self.assertEqual(vocal.id, actual_tache.vocal_id)
            self.assertEqual(vocal.user, actual_tache.user)
            self.assertEqual(vocal.date, actual_tache.date)
            self.assertIsNotNone(actual_tache.ferme)
            self.assertEqual(expected_tache["duree_minutes"], actual_tache.duree_minutes)
            self.assertEqual(expected_tache["quantite"], actual_tache.quantite)
            self.assertEqual(expected_tache["commentaire"], actual_tache.commentaire)
            self.assertEqual(expected_tache["unite"] if expected_tache["unite"] != '' else None,
                             actual_tache.unite.nom if actual_tache.unite else None)
            self.assertEqual(len(expected_tache["cultures"]), actual_tache.cultures.count())
            for expected_culture in expected_tache["cultures"]:
                actual_culture = next(culture for culture in actual_tache.cultures.all() if culture.nom == expected_culture)
                self.assertIsNotNone(actual_culture)