import datetime
import json
import os.path

from base.models import Tache, Ferme, User
from base.models.vocal import Vocal, VocalStatut
from sebania.tests import test_fixtures
from sebania.utils.db_utils import get_ferme_for_user
from thomas_ai.tasks.extract import extract
from thomas_ai.tests.TaskTestcase import TaskTestcase


class TestExtract(TaskTestcase):
    def test_extract_ok(self):
        with open(os.path.join(self.data_directory, "expected_output.json"), "r") as output_file:
            output_data = json.loads(output_file.read())
        vocal = self.create_vocal_and_run_analyze(output_data)

        # Check vocal
        self.assertEqual(VocalStatut.FINISHED, vocal.get_statut())
        self.assertIsNotNone(vocal.finished_at)

        # Check taches
        taches = Tache.objects.filter(vocal_id=vocal.id)
        self.assertEqual(len(taches), len(output_data))
        for expected_tache in output_data:
            actual_tache = next(tache for tache in taches if tache.activite.nom == expected_tache["activite"])
            self.assertIsNotNone(actual_tache, "L'activite {} n'a pas été trouvé dans la sortie".format(expected_tache["activite"]))
            self.assertEqual(vocal.id, actual_tache.vocal_id)
            self.assertEqual(vocal.user, actual_tache.user)
            self.assertEqual(vocal.date, actual_tache.date)
            self.assertIsNotNone(actual_tache.ferme)
            self.assertEqual(expected_tache["duree_minutes"], actual_tache.duree_minutes)
            self.assertEqual(expected_tache["commentaire"], actual_tache.commentaire)
            self.assertEqual(len(expected_tache["cultures"]), actual_tache.cultures.count())
            for expected_culture in expected_tache["cultures"]:
                actual_culture = next(
                    culture for culture in actual_tache.cultures.all() if culture.culture.nom == expected_culture["nom"])
                self.assertIsNotNone(actual_culture, "La culture {} n'a pas été trouvée dans la sortie".format(expected_culture["nom"]))
                self.assertEqual(expected_culture["quantite"], actual_culture.quantite)
                self.assertEqual(expected_culture["unite"] if expected_culture["unite"] != '' else None,
                             actual_culture.unite.nom if actual_culture.unite else None)
                for expected_parcelle in expected_culture["parcelles"]:
                    actual_parcelle = next(parcelle for parcelle in actual_culture.parcelles.all() if parcelle.nom == expected_parcelle)
                    self.assertIsNotNone(actual_parcelle, "La parcelle {} n'a pas été trouvée dans la sortie".format(expected_parcelle))

    def create_vocal_and_run_analyze(self, output: {}) -> Vocal:
        self.create_user_and_ferme()
        vocal = Vocal.objects.create(user=self.get_current_user(), date=datetime.datetime.now(), output=output)
        extract.now(vocal_id=vocal.id)
        vocal.refresh_from_db()
        return vocal

    def assert_tache_equal(self, vocal: Vocal, expected_tache: Tache, expected_cultures: list, expected_parcelles: list):
        if expected_tache is None:
            self.assertEqual(Tache.objects.filter(vocal_id=vocal.id).count(), 0)
            return
        actual_tache = Tache.objects.get(vocal_id=vocal.id)
        self.assertEqual(expected_tache.activite_id, actual_tache.activite_id)
        self.assertEqual(expected_tache.duree_minutes, actual_tache.duree_minutes)
        self.assertEqual(expected_tache.quantite, actual_tache.quantite)
        self.assertEqual(expected_tache.unite_id, actual_tache.unite_id)
        self.assertEqual(expected_tache.commentaire, actual_tache.commentaire)
        for expected_culture_id in expected_cultures:
            actual_culture = next(culture for culture in actual_tache.cultures.all() if culture.id == expected_culture_id)
            self.assertIsNotNone(actual_culture)
        for expected_parcelle_id in expected_parcelles:
            actual_parcelle = next(parcelle for parcelle in actual_tache.parcelles.all() if parcelle.id == expected_parcelle_id)
            self.assertIsNotNone(actual_parcelle)

    def create_user_and_ferme(self) -> Ferme:
        if self.get_current_user() is None:
            ferme = test_fixtures.create_ferme(self.init_current_user())
        else:
            ferme = get_ferme_for_user(self.get_current_user().id)
        return ferme


    def create_parcelle(self, nom_parcelle) -> int:
        ferme = self.create_user_and_ferme()
        parcelle = test_fixtures.create_parcelle(ferme=ferme, nom=nom_parcelle)
        return parcelle.id

    def test_extract_ok_cultures_parcelles(self):
        output = [
            {
                "activite": "gestion des bioagresseurs",
                "duree_minutes": 20,
                "parcelles": ["serre 1", "jardin"],
                "cultures": ["céleri branche", "blette", "poireau"],
                "quantite": 9,
                "unite": "litres",
                "commentaire": ""
            },
        ]
        expected_tache = Tache(activite_id=10, duree_minutes=20, quantite=9, unite_id=14, commentaire="")
        expected_cultures = [6, 19, 35]
        expected_parcelles = [self.create_parcelle("Serre 1"), self.create_parcelle("Jardin")]
        vocal = self.create_vocal_and_run_analyze(output)
        self.assert_tache_equal(vocal, expected_tache, expected_cultures, expected_parcelles)

    def test_extract_nok_cultures(self):
        output = [
            {
                "activite": "gestion des bioagresseurs",
                "duree_minutes": 20,
                "parcelles": ["serre 1", "jardin"],
                "cultures": ["céleri branche", "Amandes", "poireau"],
                "quantite": 9,
                "unite": "litres",
                "commentaire": ""
            },
        ]
        expected_tache = Tache(activite_id=10, duree_minutes=20, quantite=9, unite_id=14, commentaire="")
        expected_cultures = [19, 35]
        expected_parcelles = [self.create_parcelle("Serre 1"), self.create_parcelle("Jardin")]
        vocal = self.create_vocal_and_run_analyze(output)
        self.assert_tache_equal(vocal, expected_tache, expected_cultures, expected_parcelles)

    def test_extract_nok_activites(self):
        output = [
            {
                "activite": "promenade",
                "duree_minutes": 90,
                "parcelles": [],
                "cultures": [],
                "quantite": 0,
                "unite": "",
                "commentaire": ""
            },
        ]
        expected_tache = None
        vocal = self.create_vocal_and_run_analyze(output)
        self.assert_tache_equal(vocal, expected_tache, None, None)

    def test_extract_nok_parcelles(self):
        output = [
            {
                "activite": "gestion des bioagresseurs",
                "duree_minutes": 20,
                "parcelles": ["serre 1", "terasse"],
                "cultures": ["céleri branche", "blette", "poireau"],
                "quantite": 9,
                "unite": "litres",
                "commentaire": ""
            },
        ]
        expected_tache = Tache(activite_id=10, duree_minutes=20, quantite=9, unite_id=14, commentaire="")
        expected_cultures = [6, 19, 35]
        self.create_parcelle("Jardin")
        expected_parcelles = [self.create_parcelle("Serre 1")]
        vocal = self.create_vocal_and_run_analyze(output)
        self.assert_tache_equal(vocal, expected_tache, expected_cultures, expected_parcelles)

    def test_extract_ok_unites(self):
        output = [
            {
                "activite": "récolte",
                "duree_minutes": 180,
                "parcelles": ["serre 1"],
                "cultures": ["tomate"],
                "quantite": 12,
                "unite": "kg",
                "commentaire": ""
            },
        ]
        expected_tache = Tache(activite_id=17, duree_minutes=180, quantite=12, unite_id=1, commentaire="")
        expected_cultures = [43]
        expected_parcelles = [self.create_parcelle("Serre 1")]
        vocal = self.create_vocal_and_run_analyze(output)
        self.assert_tache_equal(vocal, expected_tache, expected_cultures, expected_parcelles)

    def test_extract_nok_unites(self):
        output = [
            {
                "activite": "récolte",
                "duree_minutes": 180,
                "parcelles": ["serre 1"],
                "cultures": ["tomate"],
                "quantite": 12,
                "unite": "melons",
                "commentaire": ""
            },
        ]
        expected_tache = Tache(activite_id=17, duree_minutes=180, quantite=12, commentaire="")
        expected_cultures = [43]
        expected_parcelles = [self.create_parcelle("Serre 1")]
        vocal = self.create_vocal_and_run_analyze(output)
        self.assert_tache_equal(vocal, expected_tache, expected_cultures, expected_parcelles)

    def test_extract_nok_output_bad_format(self):
        output = [
            {
                "toto": "récolte",
            },
        ]
        expected_tache = None
        vocal = self.create_vocal_and_run_analyze(output)
        self.assert_tache_equal(vocal, expected_tache, None, None)
