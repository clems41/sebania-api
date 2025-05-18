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
        output = [
            {
                "activite": "Construire",
                "duree_minutes": 180,
                "cultures": [],
                "commentaire": "Montage d'une serre chez un collègue."
            },
            {
                "activite": "Apport de MO (Amender)",
                "duree_minutes": 60,
                "cultures": [
                    {
                        "nom": "Carotte",
                        "quantite": 0,
                        "unite": "",
                        "parcelles": ["Tunnel 3"]
                    }
                ],
                "commentaire": "Installation de compost sur la planche de carotte."
            },
            {
                "activite": "Irrigation",
                "duree_minutes": 20,
                "cultures": [
                    {
                        "nom": "Carotte",
                        "quantite": 0,
                        "unite": "",
                        "parcelles": []
                    }
                ],
                "commentaire": ""
            },
            {
                "activite": "Ranger",
                "duree_minutes": 30,
                "cultures": [],
                "commentaire": "Rangement des plants."
            }
        ]
        expected_entities = [
            {
                "activite_id": 36,
                "duree_minutes": 180,
                "cultures": [],
                "parcelles": [],
                "quantite": None,
                "unite_id": None,
                "nature": None,
                "commentaire": "Montage d'une serre chez un collègue.",
                "vocal_id": "is_not_none",
            },
            {
                "activite_id": 3,
                "duree_minutes": 60,
                "cultures": [
                    {
                        "culture_id": 9,
                        "quantite": 0,
                        "unite_id": None,
                        "nature": None,
                        "parcelles": [
                            {
                                "nom": "Tunnel 3",
                            }
                        ]
                    }
                ],
                "parcelles": [],
                "quantite": None,
                "unite_id": None,
                "nature": None,
                "commentaire": "Installation de compost sur la planche de carotte.",
                "vocal_id": "is_not_none",
            },
            {
                "activite_id": 11,
                "duree_minutes": 20,
                "cultures": [
                    {
                        "culture_id": 9,
                        "quantite": 0,
                        "unite_id": None,
                        "nature": None,
                        "parcelles": []
                    }
                ],
                "parcelles": [],
                "quantite": None,
                "unite_id": None,
                "nature": None,
                "commentaire": "",
                "vocal_id": "is_not_none",
            },
            {
                "activite_id": 33,
                "duree_minutes": 30,
                "cultures": [],
                "parcelles": [],
                "quantite": None,
                "unite_id": None,
                "nature": None,
                "commentaire": "Rangement des plants.",
                "vocal_id": "is_not_none"
            }
        ]
        self._run_testcase(output, expected_entities, parcelles_to_create=["Tunnel 1", "Tunnel 2", "Tunnel 3"])

    def test_extract_ok_cultures_parcelles(self):
        output = [
            {
                "activite": "gestion des bioagresseurs",
                "duree_minutes": 20,
                "cultures": [
                    {
                        "nom": "céleri branche",
                        "quantite": 9,
                        "unite": "litres",
                        "parcelles": ["serre 1", "jardin"]
                    },
                    {
                        "nom": "blette",
                        "quantite": 0,
                        "unite": "",
                        "parcelles": ["serre 2"]
                    },
                    {
                        "nom": "poireau",
                        "quantite": 0,
                        "unite": "",
                        "parcelles": ["jardin"]
                    }
                ],
                "commentaire": ""
            },
        ]
        expected_entities = [
            {
                "activite_id": 10,
                "duree_minutes": 20,
                "cultures": [
                    {
                        "culture_id": 19,
                        "quantite": 9,
                        "unite_id": 14,
                        "nature": None,
                        "parcelles": [
                            {
                                "nom": "Serre 1",
                            },
                            {
                                "nom": "Jardin",
                            }
                        ]
                    },
                    {
                        "culture_id": 6,
                        "quantite": 0,
                        "unite_id": None,
                        "nature": None,
                        "parcelles": [
                            {
                                "nom": "Serre 2",
                            }
                        ]
                    },
                    {
                        "culture_id": 35,
                        "quantite": 0,
                        "unite_id": None,
                        "nature": None,
                        "parcelles": [
                            {
                                "nom": "Jardin",
                            }
                        ]
                    }
                ],
                "parcelles": [],
                "quantite": None,
                "unite_id": None,
                "nature": None,
                "commentaire": "",
                "vocal_id": "is_not_none"
            }
        ]
        self._run_testcase(output, expected_entities, parcelles_to_create=["Serre 1", "Serre 2", "Jardin"])

    def test_extract_nok_cultures(self):
        output = [
            {
                "activite": "gestion des bioagresseurs",
                "duree_minutes": 20,
                "cultures": [
                    {
                        "nom": "céleri branche",
                        "quantite": 9,
                        "unite": "litres",
                        "parcelles": ["serre 1", "jardin"]
                    },
                    {
                        "nom": "Amandes",
                        "quantite": 0,
                        "unite": "",
                        "parcelles": ["serre 2"]
                    },
                    {
                        "nom": "poireau",
                        "quantite": 0,
                        "unite": "",
                        "parcelles": ["jardin"]
                    }
                ],
                "commentaire": ""
            },
        ]
        expected_entities = [
            {
                "activite_id": 10,
                "duree_minutes": 20,
                "cultures": [
                    {
                        "culture_id": 19,
                        "quantite": 9,
                        "unite_id": 14,
                        "nature": None,
                        "parcelles": [
                            {
                                "nom": "Serre 1",
                            },
                            {
                                "nom": "Jardin",
                            }
                        ]
                    },
                    {
                        "culture_id": 35,
                        "quantite": 0,
                        "unite_id": None,
                        "nature": None,
                        "parcelles": [
                            {
                                "nom": "Jardin",
                            }
                        ]
                    }
                ],
                "parcelles": [],
                "quantite": None,
                "unite_id": None,
                "nature": None,
                "commentaire": "",
                "vocal_id": "is_not_none"
            }
        ]
        self._run_testcase(output, expected_entities, parcelles_to_create=["Serre 1", "Serre 2", "Jardin"])

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
        self._run_testcase(output, expected_entities, parcelles_to_create=["Tunnel 1", "Tunnel 2", "Tunnel 3"])

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
        self._run_testcase(output, expected_entities, parcelles_to_create=["Tunnel 1", "Tunnel 2", "Tunnel 3"])

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
        self._run_testcase(output, expected_entities, parcelles_to_create=["Tunnel 1", "Tunnel 2", "Tunnel 3"])

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
        self._run_testcase(output, expected_entities, parcelles_to_create=["Tunnel 1", "Tunnel 2", "Tunnel 3"])

    def test_extract_nok_output_bad_format(self):
        output = [
            {
                "toto": "récolte",
            },
        ]
        self._run_testcase(output, None, parcelles_to_create=["Tunnel 1", "Tunnel 2", "Tunnel 3"])

    def _run_testcase(self, output: {}, expected_entities, parcelles_to_create=None):
        self._create_user_and_ferme()
        if parcelles_to_create is not None:
            for parcelle_nom in parcelles_to_create:
                self._create_parcelle(parcelle_nom)
        vocal = Vocal.objects.create(user=self.get_current_user(), date=datetime.datetime.now(), output=output)
        extract.now(vocal_id=vocal.id)
        vocal.refresh_from_db()

        # Check vocal
        self.assertEqual(VocalStatut.FINISHED, vocal.get_statut())
        self.assertIsNotNone(vocal.finished_at)

        # Check taches
        taches = Tache.objects.filter(vocal_id=vocal.id).all().order_by("created_at")
        expected_nb_taches = 0
        if expected_entities is not None:
            expected_nb_taches = len(expected_entities)
        self.assertEqual(len(taches), expected_nb_taches)
        for idx, expected_entity in enumerate(expected_entities):
            entity = taches[idx]
            self.check_entity(expected_entity, entity)

    def _create_user_and_ferme(self) -> Ferme:
        if self.get_current_user() is None:
            ferme = test_fixtures.create_ferme(self.init_current_user())
        else:
            ferme = get_ferme_for_user(self.get_current_user().id)
        return ferme

    def _create_parcelle(self, nom_parcelle) -> int:
        ferme = self._create_user_and_ferme()
        parcelle = test_fixtures.create_parcelle(ferme=ferme, nom=nom_parcelle)
        return parcelle.id
