test_ok_champs_manquants = {
    "request": {
        "date": "04/04/2025",
        "activite_id": 5,
        "user_id": None,  # surcharger avant l'envoi des requêtes
        "duree_minutes": 90,
        "cultures": []
    },
    "expected_response": {
        "date": "04/04/2025",
        "activite": {
            "id": 5,
            "nom": "Paillage",
            "need_culture": True
        },
        "user": {},  # pas utiliser lors des contrôles
        "duree_minutes": 90,
        "cultures": [],
        "commentaire": None,
        "parcelles": [],
        "quantite": None,
        "unite": None,
        "nature": None,
        "fields_are_missing": True,
        "vocal_id": None
    },
    "parcelles_to_create": ["Tunnel 1", "Tunnel 2", "Tunnel 3"],
}

test_ok_simple = {
    "request": {
        "date": "04/04/2025",
        "activite_id": 5,
        "user_id": None,  # surcharger avant l'envoi des requêtes
        "duree_minutes": 90,
        "cultures": [],
        "commentaire": "Mon petit commentaire éàô",
        "parcelle_ids": [],
        "nature": None,
        "quantite": None,
        "unite_id": None
    },
    "expected_response": {
        "date": "04/04/2025",
        "activite": {
            "id": 5,
            "nom": "Paillage",
            "need_culture": True
        },
        "user": {},  # pas utiliser lors des contrôles
        "duree_minutes": 90,
        "cultures": [],
        "commentaire": "Mon petit commentaire éàô",
        "parcelles": [],
        "quantite": None,
        "unite": None,
        "nature": None,
        "fields_are_missing": True,
        "vocal_id": None
    },
    "parcelles_to_create": ["Tunnel 1", "Tunnel 2", "Tunnel 3"],
}

test_ok_simple_complet = {
    "request": {
        "date": "04/04/2025",
        "activite_id": 3,
        "user_id": None,
        "duree_minutes": 20,
        "cultures": [],
        "commentaire": "Mon petit commentaire éàô",
        "parcelle_ids": [1, 2],
        "quantite": 12,
        "nature": "Montagne",
        "unite_id": 16
    },
    "expected_response": {
        "date": "04/04/2025",
        "activite": {
            "id": 3,
            "nom": "Apport de MO (Amender)",
            "need_culture": True
        },
        "user": {},  # pas utiliser lors des contrôles
        "duree_minutes": 20,
        "cultures": [],
        "commentaire": "Mon petit commentaire éàô",
        "parcelles": [
            {
                "nom": "Tunnel 1",
            },
            {
                "nom": "Tunnel 2",
            }
        ],
        "quantite": 12.0,
        "unite": {
            "id": 16,
            "nom": "brouettes",
            "recolte_compatible": False,
        },
        "nature": "Montagne",
        "fields_are_missing": True,
        "vocal_id": None
    },
    "parcelles_to_create": ["Tunnel 1", "Tunnel 2", "Tunnel 3"],
}

test_ok_avec_cultures = {
    "request": {
        "date": "04/04/2025",
        "activite_id": 3,
        "user_id": None,
        "duree_minutes": 20,
        "cultures": [
            {
                "culture_id": 8,
                "parcelle_ids": [1, 3],
                "quantite": 12,
                "nature": "Montagne",
                "unite_id": 16
            },
            {
                "culture_id": 12,
                "parcelle_ids": [2],
                "quantite": 12,
                "nature": "",
                "unite_id": 1
            }
        ],
        "commentaire": "Mon petit commentaire éàô",
        "parcelle_ids": [],
        "quantite": None,
        "nature": "",
        "unite_id": None
    },
    "expected_response": {
        "date": "04/04/2025",
        "activite": {
            "id": 3,
            "nom": "Apport de MO (Amender)",
            "need_culture": True
        },
        "user": {},  # pas utiliser lors des contrôles
        "duree_minutes": 20,
        "cultures": [
            {
                "culture": {
                    "id": 8,
                    "nom": "Butternut"
                },
                "parcelles": [
                    {
                        "nom": "Tunnel 1",
                    },
                    {
                        "nom": "Tunnel 3",
                    }
                ],
                "quantite": 12.0,
                "unite": {
                    "id": 16,
                    "nom": "brouettes",
                    "recolte_compatible": False,
                },
                "nature": "Montagne",
            },
            {
                "culture": {
                    "id": 12,
                    "nom": "Chou kale"
                },
                "parcelles": [
                    {
                        "nom": "Tunnel 2",
                    }
                ],
                "quantite": 12.0,
                "unite": {
                    "id": 1,
                    "nom": "kg",
                    "recolte_compatible": True,
                },
                "nature": "",
            }
        ],
        "commentaire": "Mon petit commentaire éàô",
        "parcelles": [],
        "quantite": None,
        "unite": None,
        "nature": "",
        "fields_are_missing": False,
        "vocal_id": None
    },
    "parcelles_to_create": ["Tunnel 1", "Tunnel 2", "Tunnel 3"],
}

test_ok_avec_cultures_complet = {
    "request": {
        "date": "04/04/2025",
        "activite_id": 3,
        "user_id": None,
        "duree_minutes": 20,
        "cultures": [
            {
                "culture_id": 5,
                "parcelle_ids": [1, 3],
                "quantite": 12,
                "nature": "Montagne",
                "unite_id": 16
            },
            {
                "culture_id": 21,
                "parcelle_ids": [2],
                "quantite": 52.3,
                "nature": "",
                "unite_id": 1
            }
        ],
        "commentaire": "Mon petit commentaire éàô",
        "parcelle_ids": [1, 2],
        "quantite": 12,
        "nature": "Montagne",
        "unite_id": 16
    },
    "expected_response": {
        "date": "04/04/2025",
        "activite": {
            "id": 3,
            "nom": "Apport de MO (Amender)",
            "need_culture": True
        },
        "user": {},  # pas utiliser lors des contrôles
        "duree_minutes": 20,
        "cultures": [
            {
                "culture": {
                    "id": 5,
                    "nom": "Betterave"
                },
                "parcelles": [
                    {
                        "nom": "Tunnel 1",
                    },
                    {
                        "nom": "Tunnel 3",
                    }
                ],
                "quantite": 12.0,
                "unite": {
                    "id": 16,
                    "nom": "brouettes",
                    "recolte_compatible": False,
                },
                "nature": "Montagne",
            },
            {
                "culture": {
                    "id": 21,
                    "nom": "Endive"
                },
                "parcelles": [
                    {
                        "nom": "Tunnel 2",
                    }
                ],
                "quantite": 52.3,
                "unite": {
                    "id": 1,
                    "nom": "kg",
                    "recolte_compatible": True,
                },
                "nature": "",
            }
        ],
        "commentaire": "Mon petit commentaire éàô",
        "parcelles": [
            {
                "nom": "Tunnel 1",
            },
            {
                "nom": "Tunnel 2",
            }
        ],
        "quantite": 12.0,
        "unite": {
            "id": 16,
            "nom": "brouettes",
            "recolte_compatible": False,
        },
        "nature": "Montagne",
        "fields_are_missing": False,
        "vocal_id": None
    },
    "parcelles_to_create": ["Tunnel 1", "Tunnel 2", "Tunnel 3"],
}
