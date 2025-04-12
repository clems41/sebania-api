from base.models.statut import StatutTache
from sebania.tests import test_fixtures
from sebania.tests.SebaniaTestCase import SebaniaTestCase


class TestStatut(SebaniaTestCase):
    def test_statut_ok(self):
        responsable = test_fixtures.create_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        tache = test_fixtures.create_tache(ferme=ferme, user_id=responsable.id, nb_parcelles=2, culture_id=3, activite_id=3)
        self.assertEqual(tache.get_statut(), StatutTache.OK)

    def test_statut_ok_sans_cultures(self):
        responsable = test_fixtures.create_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        tache = test_fixtures.create_tache(ferme=ferme, user_id=responsable.id, nb_parcelles=0, culture_id=None, activite_id=30)
        self.assertEqual(tache.get_statut(), StatutTache.OK)

    def test_statut_warning_parcelles(self):
        responsable = test_fixtures.create_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        tache = test_fixtures.create_tache(ferme=ferme, user_id=responsable.id, nb_parcelles=2, culture_id=None, activite_id=3)
        self.assertEqual(tache.get_statut(), StatutTache.WARNING)

    def test_statut_warning_culture(self):
        responsable = test_fixtures.create_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        tache = test_fixtures.create_tache(ferme=ferme, user_id=responsable.id, nb_parcelles=0, culture_id=3, activite_id=3)
        self.assertEqual(tache.get_statut(), StatutTache.WARNING)

    def test_statut_danger(self):
        responsable = test_fixtures.create_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        tache = test_fixtures.create_tache(ferme=ferme, user_id=responsable.id, nb_parcelles=0, culture_id=None, activite_id=3)
        self.assertEqual(tache.get_statut(), StatutTache.DANGER)