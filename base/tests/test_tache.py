import datetime
import json
from typing import List

from django.urls import reverse_lazy
from rest_framework import status

from base.models import User, Ferme, Tache, Parcelle
from sebania.tests import test_fixtures
from sebania.tests.SebaniaTestCase import SebaniaTestCase
from sebania.utils import crypto_utils


def _get_url_detail(tache_id: int):
    return reverse_lazy('taches-detail', args=[tache_id])

class TestTache(SebaniaTestCase):
    url = None
    
    def _check_response(self, request, response):
        response_data = json.loads(response.content)
        self.assertIsNotNone(response_data.get("id"))
        self.assertEqual(response_data.get("date"), request.get("date"))
        self.assertEqual(response_data.get("activite").get("id"), request.get("activite_id"))
        self.assertIsNotNone(response_data.get("activite").get("nom"))
        self.assertEqual(response_data.get("user").get("id"), request.get("user_id"))
        self.assertIsNotNone(response_data.get("user").get("email"))
        self.assertEqual(response_data.get("duree_minutes"), request.get("duree_minutes"))
        self.assertEqual(response_data.get("quantite_recoltee"), request.get("quantite_recoltee"))
        self.assertEqual(response_data.get("commentaire"), request.get("commentaire"))
        if request.get("culture_id") is not None:
            culture = response_data.get("culture")
            self.assertEqual(culture.get("id"), request.get("culture_id"))
            self.assertIsNotNone(culture.get("nom"))
        if request.get("parcelle_ids") is not None:
            self.assertEqual(len(response_data.get("parcelles")), len(request.get("parcelle_ids")))
            for parcelle in response_data.get("parcelles"):
                self.assertTrue(parcelle.get("id") in request.get("parcelle_ids"))
                self.assertIsNotNone(parcelle.get("nom"))

    def _check_database(self, request, response, ferme):
        response_data = json.loads(response.content)
        tache_id = response_data.get("id")
        tache = Tache.objects.get(id=tache_id)
        self.assertEqual(tache.date.strftime("%d/%m/%Y"), request.get("date"))
        self.assertEqual(tache.activite_id, request.get("activite_id"))
        self.assertEqual(tache.user_id, request.get("user_id"))
        self.assertEqual(tache.duree_minutes, request.get("duree_minutes"))
        self.assertEqual(tache.quantite_recoltee, request.get("quantite_recoltee"))
        self.assertEqual(tache.commentaire, request.get("commentaire"))
        self.assertEqual(tache.culture_id, request.get("culture_id"))
        if request.get("parcelle_ids") is not None:
            self.assertEqual(tache.parcelles.count(), len(request.get("parcelle_ids")))
            for parcelle in tache.parcelles.all():
                self.assertTrue(parcelle.id in request.get("parcelle_ids"))
            self.assertEqual(tache.ferme, ferme)

    def _create_or_update(self, tache_id: int = None, date: str = datetime.date.today().strftime("%d/%m/%Y"), activite_id: int = 1, user: User = None,
                ferme: Ferme = None, duree_minutes = 90, culture_id: int = None, commentaire: str = None,
                parcelle_ids: List[int] = None, quantite_recoltee: int = None, expected_status_code=status.HTTP_201_CREATED):
        if user is None:
            user = self.init_current_user()
        if ferme is None:
            ferme = test_fixtures.create_ferme(responsable=user)
        request = {
            'date': date,
            'activite_id': activite_id,
            'user_id': user.id,
            'duree_minutes': duree_minutes,
            'culture_id': culture_id,
            'parcelle_ids': parcelle_ids,
            'quantite_recoltee': quantite_recoltee,
            'commentaire': commentaire,
        }
        if tache_id is not None:
            # request["id"] = tache_id
            response = self.client.put(_get_url_detail(tache_id), request, format='json', headers=self.get_jwt_headers())
        else:
            response = self.client.post(self.url, request, format='json', headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, expected_status_code)
        if expected_status_code <= status.HTTP_201_CREATED:
            self._check_response(request, response)
            self._check_database(request, response, ferme)
        elif tache_id is None:
            # Il faut vérifier que la tâche n'a pas été créée en base (uniquement lors de la création)
            taches = Tache.objects.filter(user=user, ferme=ferme).all()
            self.assertTrue(len(taches) == 0)

class TestCreationTache(TestTache):
    url = reverse_lazy('taches-list')
    
    def test_ok_creation_sans_cultures(self):
        self._create_or_update()
    
    def test_ok_creation_complet(self):
        user = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=user, nb_parcelles=3)
        self._create_or_update(culture_id=1, parcelle_ids=[ferme.parcelle_set.all()[0].id], user=user, ferme=ferme, commentaire=crypto_utils.random_string(length=350))
    
    def test_ok_creation_avec_culture(self):
        user = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=user, nb_parcelles=3)
        self._create_or_update(culture_id=1, user=user, ferme=ferme)
    
    def test_ok_creation_avec_parcelles(self):
        user = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=user, nb_parcelles=3)
        self._create_or_update(parcelle_ids=[ferme.parcelle_set.all()[0].id], user=user, ferme=ferme)
    
    def test_ok_creation_employe(self):
        responsable = test_fixtures.create_user()
        employe = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable, employes=[employe])
        self._create_or_update(user=employe, ferme=ferme)
    
    def test_ok_creation_responsable_pour_employe(self):
        responsable = self.init_current_user()
        employe = test_fixtures.create_user()
        ferme = test_fixtures.create_ferme(responsable=responsable, employes=[employe])
        self._create_or_update(user=employe, ferme=ferme)

    def test_nok_creation_user_not_exists(self):
        responsable = self.init_current_user()
        user_not_existing = User(first_name=crypto_utils.random_string(length=50), last_name=crypto_utils.random_string(length=50), email=crypto_utils.random_email(), id=99)
        ferme = test_fixtures.create_ferme(responsable=responsable)
        self._create_or_update(user=user_not_existing, ferme=ferme, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_creation_user_not_in_ferme(self):
        responsable = self.init_current_user()
        user_not_in_ferme = test_fixtures.create_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        self._create_or_update(user=user_not_in_ferme, ferme=ferme, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_creation_activite_not_exists(self):
        self._create_or_update(activite_id=698754, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_creation_culture_not_exists(self):
        self._create_or_update(culture_id=3652, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_creation_parcelle_not_exists(self):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        not_existing_parcelle = Parcelle(nom=crypto_utils.random_string(), superficie=120, type_id=1, ferme=ferme, id=23)
        parcelles = [test_fixtures.create_parcelle(ferme), not_existing_parcelle, test_fixtures.create_parcelle(ferme)]
        parcelle_ids = [parcelle.id for parcelle in parcelles]
        self._create_or_update(expected_status_code=status.HTTP_404_NOT_FOUND, user=responsable, ferme=ferme, parcelle_ids=parcelle_ids)

    def test_nok_creation_date_invalide(self):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        # mauvais jour
        self._create_or_update(expected_status_code=status.HTTP_400_BAD_REQUEST, date="35/11/2025", user=responsable, ferme=ferme)
        # mauvais mois
        self._create_or_update(expected_status_code=status.HTTP_400_BAD_REQUEST, date="23/13/2025", user=responsable, ferme=ferme)
        # mauavaise année
        self._create_or_update(expected_status_code=status.HTTP_400_BAD_REQUEST, date="23/11/652", user=responsable, ferme=ferme)

    def test_nok_creation_duree_invalide(self):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        # négatif
        self._create_or_update(expected_status_code=status.HTTP_400_BAD_REQUEST, duree_minutes=-12, user=responsable, ferme=ferme)
        # 0
        self._create_or_update(expected_status_code=status.HTTP_400_BAD_REQUEST, duree_minutes=0, user=responsable, ferme=ferme)
        # supérieur au nombre de minutes dans une journée
        self._create_or_update(expected_status_code=status.HTTP_400_BAD_REQUEST, duree_minutes=60*24 + 1, user=responsable, ferme=ferme)

    def test_nok_creation_employe_pour_responsable(self):
        responsable = test_fixtures.create_user()
        employe = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable, employes=[employe])
        self._create_or_update(expected_status_code=status.HTTP_403_FORBIDDEN, user=responsable, ferme=ferme)

    def test_nok_creation_employe_pour_autre_employe(self):
        responsable = test_fixtures.create_user()
        employe = self.init_current_user()
        other_employe = test_fixtures.create_user()
        ferme = test_fixtures.create_ferme(responsable=responsable, employes=[employe, other_employe])
        self._create_or_update(expected_status_code=status.HTTP_403_FORBIDDEN, user=other_employe, ferme=ferme)


class TestUpdateTache(TestTache):
    url = reverse_lazy('taches-detail')

    def _update(self, tache_id: int = None, date: str = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%d/%m/%Y"), activite_id: int = 5, user: User = None,
                ferme: Ferme = None, duree_minutes = 230, culture_id: int = None, commentaire: str = None,
                parcelle_ids: List[int] = None, quantite_recoltee: int = None, expected_status_code=status.HTTP_200_OK):
        if user is None:
            user = self.init_current_user()
        if ferme is None:
            ferme = test_fixtures.create_ferme(responsable=user)
        if tache_id is None:
            tache = test_fixtures.create_tache(user_id=user.id, ferme=ferme)
            tache_id = tache.id
        return self._create_or_update(tache_id=tache_id, date=date, activite_id=activite_id,
                                      user=user, ferme=ferme, duree_minutes=duree_minutes, culture_id=culture_id, commentaire=commentaire,
                                      parcelle_ids=parcelle_ids, quantite_recoltee=quantite_recoltee, expected_status_code=expected_status_code)

    
    def test_ok_update_sans_cultures(self):
        self._update()
    
    def test_ok_update_complet(self):
        user = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=user, nb_parcelles=3)
        self._update(culture_id=8, parcelle_ids=[ferme.parcelle_set.all()[2].id], user=user, ferme=ferme, commentaire=crypto_utils.random_string(length=350))
    
    def test_ok_update_avec_culture(self):
        user = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=user, nb_parcelles=3)
        self._update(culture_id=9, user=user, ferme=ferme)
    
    def test_ok_update_avec_parcelles(self):
        user = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=user, nb_parcelles=3)
        self._update(parcelle_ids=[ferme.parcelle_set.all()[1].id], user=user, ferme=ferme)
    
    def test_ok_update_employe(self):
        responsable = test_fixtures.create_user()
        employe = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable, employes=[employe])
        self._update(user=employe, ferme=ferme)
    
    def test_ok_update_responsable_pour_employe(self):
        responsable = self.init_current_user()
        employe = test_fixtures.create_user()
        ferme = test_fixtures.create_ferme(responsable=responsable, employes=[employe])
        self._update(user=employe, ferme=ferme)

    def test_nok_update_tache_not_exists(self):
        self._update(tache_id=99, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_update_user_not_exists(self):
        responsable = self.init_current_user()
        user_not_existing = User(first_name=crypto_utils.random_string(length=50), last_name=crypto_utils.random_string(length=50), email=crypto_utils.random_email(), id=99)
        ferme = test_fixtures.create_ferme(responsable=responsable)
        existing_tache = test_fixtures.create_tache(user_id=responsable.id, ferme=ferme)
        self._update(tache_id=existing_tache.id, user=user_not_existing, ferme=ferme, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_update_user_not_in_ferme(self):
        responsable = self.init_current_user()
        user_not_in_ferme = test_fixtures.create_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        self._update(user=user_not_in_ferme, ferme=ferme, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_update_activite_not_exists(self):
        self._update(activite_id=698754, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_update_culture_not_exists(self):
        self._update(culture_id=3652, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_update_parcelle_not_exists(self):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable, nb_parcelles=3)
        not_existing_parcelle = Parcelle(nom=crypto_utils.random_string(), superficie=120, type_id=1, ferme=ferme, id=153)
        parcelles = [test_fixtures.create_parcelle(ferme), not_existing_parcelle, test_fixtures.create_parcelle(ferme)]
        parcelle_ids = [parcelle.id for parcelle in parcelles]
        self._update(expected_status_code=status.HTTP_404_NOT_FOUND, user=responsable, ferme=ferme, parcelle_ids=parcelle_ids)

    def test_nok_update_date_invalide(self):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        # mauvais jour
        self._update(expected_status_code=status.HTTP_400_BAD_REQUEST, date="35/11/2025", user=responsable, ferme=ferme)
        # mauvais mois
        self._update(expected_status_code=status.HTTP_400_BAD_REQUEST, date="23/13/2025", user=responsable, ferme=ferme)
        # mauavaise année
        self._update(expected_status_code=status.HTTP_400_BAD_REQUEST, date="23/11/652", user=responsable, ferme=ferme)

    def test_nok_update_duree_invalide(self):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        # négatif
        self._update(expected_status_code=status.HTTP_400_BAD_REQUEST, duree_minutes=-12, user=responsable, ferme=ferme)
        # 0
        self._update(expected_status_code=status.HTTP_400_BAD_REQUEST, duree_minutes=0, user=responsable, ferme=ferme)
        # supérieur au nombre de minutes dans une journée
        self._update(expected_status_code=status.HTTP_400_BAD_REQUEST, duree_minutes=60*24 + 1, user=responsable, ferme=ferme)

    def test_nok_update_employe_pour_responsable(self):
        responsable = test_fixtures.create_user()
        employe = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable, employes=[employe])
        self._update(expected_status_code=status.HTTP_403_FORBIDDEN, user=responsable, ferme=ferme)

    def test_nok_update_employe_pour_autre_employe(self):
        responsable = test_fixtures.create_user()
        employe = self.init_current_user()
        other_employe = test_fixtures.create_user()
        ferme = test_fixtures.create_ferme(responsable=responsable, employes=[employe, other_employe])
        self._update(expected_status_code=status.HTTP_403_FORBIDDEN, user=other_employe, ferme=ferme)