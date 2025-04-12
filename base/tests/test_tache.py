import calendar
import datetime
import json
import random
from typing import List

from django.urls import reverse_lazy
from django.utils import timezone
from rest_framework import status

from base.models import User, Ferme, Tache, Parcelle, user
from base.models.statut import StatutTache
from sebania.tests import test_fixtures
from sebania.tests.SebaniaTestCase import SebaniaTestCase
from sebania.utils import crypto_utils


def _get_url_detail(tache_id: int):
    return reverse_lazy('taches-detail', args=[tache_id])


class TestTache(SebaniaTestCase):
    url = reverse_lazy('taches-list')

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
        self.assertEqual(response_data.get("nature"), request.get("nature"))
        self.assertEqual(response_data.get("quantite"), request.get("quantite"))
        self.assertEqual(response_data.get("unite"), request.get("unite"))
        expected_statut = StatutTache.DANGER
        if request.get("culture_id") is not None:
            culture = response_data.get("culture")
            self.assertEqual(culture.get("id"), request.get("culture_id"))
            self.assertIsNotNone(culture.get("nom"))
            expected_statut = StatutTache.WARNING
        if request.get("parcelle_ids") is not None:
            self.assertEqual(len(response_data.get("parcelles")), len(request.get("parcelle_ids")))
            for parcelle in response_data.get("parcelles"):
                self.assertTrue(parcelle.get("id") in request.get("parcelle_ids"))
                self.assertIsNotNone(parcelle.get("nom"))
            expected_statut = StatutTache.WARNING
        # check statut
        if request.get("culture_id") is not None and request.get("parcelle_ids") is not None:
            expected_statut = StatutTache.OK
        self.assertEqual(response_data.get("statut"), expected_statut.name)

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
        self.assertEqual(tache.unite, request.get("unite"))
        self.assertEqual(tache.nature, request.get("nature"))
        self.assertEqual(tache.quantite, request.get("quantite"))
        if request.get("parcelle_ids") is not None:
            self.assertEqual(tache.parcelles.count(), len(request.get("parcelle_ids")))
            for parcelle in tache.parcelles.all():
                self.assertTrue(parcelle.id in request.get("parcelle_ids"))
            self.assertEqual(tache.ferme, ferme)

    def _create_or_update(self, tache_id: int = None, date: str = datetime.date.today().strftime("%d/%m/%Y"),
                          activite_id: int = 1, user: User = None,
                          ferme: Ferme = None, duree_minutes=90, culture_id: int = None, commentaire: str = None,
                          parcelle_ids: List[int] = None, quantite_recoltee: int = None, quantite: float = None, unite: str = None, nature: str = None,
                          expected_status_code=status.HTTP_201_CREATED):
        if user is None:
            user = self.init_current_user()
        if ferme is None:
            ferme = test_fixtures.create_ferme(responsable=user)
        request = {
            "date": date,
            "activite_id": activite_id,
            "user_id": user.id,
            "duree_minutes": duree_minutes,
            "culture_id": culture_id,
            "parcelle_ids": parcelle_ids,
            "quantite_recoltee": quantite_recoltee,
            "commentaire": commentaire,
            "nature": nature,
            "unite": unite,
            "quantite": quantite,
        }
        if tache_id is not None:
            response = self.client.put(_get_url_detail(tache_id), request, format='json',
                                       headers=self.get_jwt_headers())
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
    def test_ok_creation_sans_cultures(self):
        self._create_or_update()

    def test_ok_creation_complet(self):
        user = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=user, nb_parcelles=3)
        self._create_or_update(culture_id=1, parcelle_ids=[ferme.parcelle_set.all()[0].id], user=user, ferme=ferme,
                               commentaire=crypto_utils.random_string(length=350), quantite=142.3,
                               unite=crypto_utils.random_string(length=10), nature=crypto_utils.random_string(length=25))

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
        user_not_existing = User(first_name=crypto_utils.random_string(length=50),
                                 last_name=crypto_utils.random_string(length=50), email=crypto_utils.random_email(),
                                 id=99)
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
        not_existing_parcelle = Parcelle(nom=crypto_utils.random_string(), superficie=120, type_id=1, ferme=ferme,
                                         id=23)
        parcelles = [test_fixtures.create_parcelle(ferme), not_existing_parcelle, test_fixtures.create_parcelle(ferme)]
        parcelle_ids = [parcelle.id for parcelle in parcelles]
        self._create_or_update(expected_status_code=status.HTTP_404_NOT_FOUND, user=responsable, ferme=ferme,
                               parcelle_ids=parcelle_ids)

    def test_nok_creation_date_invalide(self):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        # mauvais jour
        self._create_or_update(expected_status_code=status.HTTP_400_BAD_REQUEST, date="35/11/2025", user=responsable,
                               ferme=ferme)
        # mauvais mois
        self._create_or_update(expected_status_code=status.HTTP_400_BAD_REQUEST, date="23/13/2025", user=responsable,
                               ferme=ferme)
        # mauavaise année
        self._create_or_update(expected_status_code=status.HTTP_400_BAD_REQUEST, date="23/11/652", user=responsable,
                               ferme=ferme)

    def test_nok_creation_duree_invalide(self):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        # négatif
        self._create_or_update(expected_status_code=status.HTTP_400_BAD_REQUEST, duree_minutes=-12, user=responsable,
                               ferme=ferme)
        # 0
        self._create_or_update(expected_status_code=status.HTTP_400_BAD_REQUEST, duree_minutes=0, user=responsable,
                               ferme=ferme)
        # supérieur au nombre de minutes dans une journée
        self._create_or_update(expected_status_code=status.HTTP_400_BAD_REQUEST, duree_minutes=60 * 24 + 1,
                               user=responsable, ferme=ferme)

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
    def _update(self, tache_id: int = None,
                date: str = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%d/%m/%Y"),
                activite_id: int = 5, user: User = None,
                ferme: Ferme = None, duree_minutes=230, culture_id: int = None, commentaire: str = None,
                parcelle_ids: List[int] = None, quantite_recoltee: int = None, quantite: float = None, unite: str = None, nature: str = None,
                expected_status_code=status.HTTP_200_OK):
        if user is None:
            user = self.init_current_user()
        if ferme is None:
            ferme = test_fixtures.create_ferme(responsable=user)
        if tache_id is None:
            tache = test_fixtures.create_tache(user_id=user.id, ferme=ferme, nb_parcelles=0)
            tache_id = tache.id
        return self._create_or_update(tache_id=tache_id, date=date, activite_id=activite_id,
                                      user=user, ferme=ferme, duree_minutes=duree_minutes, culture_id=culture_id,
                                      commentaire=commentaire,
                                      parcelle_ids=parcelle_ids, quantite_recoltee=quantite_recoltee,
                                      expected_status_code=expected_status_code, quantite=quantite, nature=nature, unite=unite)

    def test_ok_update_sans_cultures(self):
        self._update()

    def test_ok_update_complet(self):
        user = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=user, nb_parcelles=3)
        self._update(culture_id=8, parcelle_ids=[ferme.parcelle_set.all()[2].id], user=user, ferme=ferme,
                     commentaire=crypto_utils.random_string(length=350), quantite=142.3,
                               unite=crypto_utils.random_string(length=10), nature=crypto_utils.random_string(length=25))

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
        user_not_existing = User(first_name=crypto_utils.random_string(length=50),
                                 last_name=crypto_utils.random_string(length=50), email=crypto_utils.random_email(),
                                 id=99)
        ferme = test_fixtures.create_ferme(responsable=responsable)
        existing_tache = test_fixtures.create_tache(user_id=responsable.id, ferme=ferme)
        self._update(tache_id=existing_tache.id, user=user_not_existing, ferme=ferme,
                     expected_status_code=status.HTTP_404_NOT_FOUND)

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
        not_existing_parcelle = Parcelle(nom=crypto_utils.random_string(), superficie=120, type_id=1, ferme=ferme,
                                         id=153)
        parcelles = [test_fixtures.create_parcelle(ferme), not_existing_parcelle, test_fixtures.create_parcelle(ferme)]
        parcelle_ids = [parcelle.id for parcelle in parcelles]
        self._update(expected_status_code=status.HTTP_404_NOT_FOUND, user=responsable, ferme=ferme,
                     parcelle_ids=parcelle_ids)

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
        self._update(expected_status_code=status.HTTP_400_BAD_REQUEST, duree_minutes=60 * 24 + 1, user=responsable,
                     ferme=ferme)

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


class TestGetTache(SebaniaTestCase):
    url = reverse_lazy('taches-list')

    def _create_data(self, user: User, ferme: Ferme, date: datetime.datetime = timezone.now()):
        other_date = timezone.now() - datetime.timedelta(days=1)
        other_ferme = test_fixtures.create_ferme()
        other_user = test_fixtures.create_user()
        # création de tâches qui correspondent aux filtres
        matching_taches = []
        for _ in range(6):
            matching_taches.append(test_fixtures.create_tache(ferme=ferme, user_id=user.id, nb_parcelles=3, date=date))
        # création de tâches qui ne correspondant pas aux filtres
        for _ in range(5):
            test_fixtures.create_tache(ferme=other_ferme, user_id=user.id, nb_parcelles=3, date=date)
            test_fixtures.create_tache(ferme=ferme, user_id=other_user.id, nb_parcelles=3, date=date)
            test_fixtures.create_tache(ferme=ferme, user_id=user.id, nb_parcelles=3, date=other_date)
        return matching_taches

    def _compare_response_with_expected(self, response, expected_taches: List[Tache]):
        if len(expected_taches) == 1:
            actual_taches = [json.loads(response.content)]
        else:
            actual_taches = json.loads(response.content)
        self.assertEqual(len(actual_taches), len(expected_taches))
        for actual_tache in actual_taches:
            expected_tache = next((x for x in expected_taches if x.id == actual_tache.get("id")), None)
            self.assertIsNotNone(expected_tache)
            self.assertEqual(expected_tache.activite_id, actual_tache.get("activite").get("id"))
            self.assertEqual(expected_tache.user_id, actual_tache.get("user").get("id"))
            self.assertEqual(expected_tache.date.strftime("%d/%m/%Y"), actual_tache.get("date"))
            self.assertEqual(expected_tache.duree_minutes, actual_tache.get("duree_minutes"))
            expected_statut = StatutTache.DANGER
            if expected_tache.culture_id is not None:
                self.assertEqual(expected_tache.culture_id, actual_tache.get("culture").get("id"))
                expected_statut = StatutTache.WARNING
            self.assertEqual(expected_tache.quantite_recoltee, actual_tache.get("quantite_recoltee"))
            self.assertEqual(expected_tache.commentaire, actual_tache.get("commentaire"))
            self.assertEqual(expected_tache.nature, actual_tache.get("nature"))
            self.assertEqual(expected_tache.unite, actual_tache.get("unite"))
            self.assertEqual(expected_tache.quantite, actual_tache.get("quantite"))
            for expected_parcelle in expected_tache.parcelles.all():
                actual_parcelle = next(
                    (x for x in actual_tache.get("parcelles") if x.get("id") == expected_parcelle.id), None)
                self.assertIsNotNone(actual_parcelle)
                self.assertEqual(expected_parcelle.nom, actual_parcelle.get("nom"))
                self.assertEqual(expected_parcelle.superficie, actual_parcelle.get("superficie"))
                self.assertEqual(expected_parcelle.type_id, actual_parcelle.get("type").get("id"))
            if len(expected_tache.parcelles.all()) > 0:
                if expected_tache.culture_id is not None:
                    expected_statut = StatutTache.OK
                else:
                    expected_statut = StatutTache.WARNING
            self.assertEqual(expected_statut.name, actual_tache.get("statut"))

    def test_ok_get_one(self):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        existing_tache = test_fixtures.create_tache(ferme=ferme, user_id=responsable.id, nb_parcelles=3)
        response = self.client.get(_get_url_detail(existing_tache.id), headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._compare_response_with_expected(response, [existing_tache])

    def test_ok_get_all(self):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        existing_taches = []
        for _ in range(6):
            existing_taches.append(test_fixtures.create_tache(ferme=ferme, user_id=responsable.id, nb_parcelles=3))
        response = self.client.get(self.url, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._compare_response_with_expected(response, existing_taches)

    def test_ok_get_all_filters_date_user(self):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        date = timezone.now()
        matching_taches = self._create_data(date=date, user=responsable, ferme=ferme)
        data = {
            "user_id": responsable.id,
            "date": date.strftime("%d/%m/%Y"),
        }
        response = self.client.get(self.url, data=data, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._compare_response_with_expected(response, matching_taches)


class TestDeleteTache(SebaniaTestCase):
    def _delete(self, tache_id: int = None, user_tache: User = None, user_delete: User = None, ferme: Ferme = None,
                expected_status_code: int = status.HTTP_204_NO_CONTENT):
        if user_delete is None:
            user_delete = self.init_current_user()
        if user_tache is None:
            user_tache = user_delete
        if ferme is None:
            ferme = test_fixtures.create_ferme(responsable=user_delete)
        # Création de la tâche en base
        if tache_id is None:
            tache = test_fixtures.create_tache(ferme=ferme, user_id=user_tache.id, nb_parcelles=3)
            tache_id = tache.id
        # Suppression
        response = self.client.delete(_get_url_detail(tache_id), headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, expected_status_code)
        # Vérification que la tâche n'est plus en base
        if expected_status_code == status.HTTP_204_NO_CONTENT:
            self.assertRaises(Tache.DoesNotExist, lambda: Tache.objects.get(id=tache_id))

    def test_ok_delete(self):
        self._delete()

    def test_ok_delete_responsable_pour_employe(self):
        responsable = self.init_current_user()
        ferme = test_fixtures.create_ferme(responsable=responsable)
        employe = ferme.employes.first()
        self._delete(user_tache=employe, user_delete=responsable, ferme=ferme)

    def test_ok_delete_employe_pour_employe(self):
        employe1 = self.init_current_user()
        ferme = test_fixtures.create_ferme(employes=[employe1])
        self._delete(user_tache=employe1, user_delete=employe1, ferme=ferme)

    def test_nok_delete_id_not_exists(self):
        self._delete(tache_id=99, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_nok_delete_employe_pour_responsable(self):
        employe1 = self.init_current_user()
        responsable = test_fixtures.create_user()
        ferme = test_fixtures.create_ferme(employes=[employe1], responsable=responsable)
        self._delete(user_tache=responsable, user_delete=employe1, ferme=ferme,
                     expected_status_code=status.HTTP_403_FORBIDDEN)

    def test_nok_delete_employe_pour_autre_employe(self):
        employe1 = self.init_current_user()
        employe2 = test_fixtures.create_user()
        ferme = test_fixtures.create_ferme(employes=[employe1, employe2])
        self._delete(user_tache=employe2, user_delete=employe1, ferme=ferme,
                     expected_status_code=status.HTTP_403_FORBIDDEN)

    def test_nok_delete_responsable_pour_autre_ferme(self):
        responsable = self.init_current_user()
        autre_responsable = test_fixtures.create_user()
        test_fixtures.create_ferme(responsable=responsable)
        autre_ferme = test_fixtures.create_ferme(responsable=autre_responsable)
        self._delete(user_tache=autre_responsable, user_delete=responsable, ferme=autre_ferme,
                     expected_status_code=status.HTTP_404_NOT_FOUND)


class TestCalendrier(SebaniaTestCase):
    url = reverse_lazy('taches-calendrier')

    def _create_taches(self, date, ferme, user_tache: User):
        total = 0
        for _ in range(random.randint(4, 9)):
            duree = random.randint(30, 90)
            test_fixtures.create_tache(ferme=ferme, user_id=user_tache.id, nb_parcelles=0, duree_minutes=duree, date=date)
            total += duree
        return total

    def _create_data(self, user_concerned: User, annee: int, numero_semaine: int = None, numero_mois: int = None, ferme: Ferme = None):
        if ferme is None:
            employes = [test_fixtures.create_user(), test_fixtures.create_user(), user_concerned]
            ferme = test_fixtures.create_ferme(responsable=test_fixtures.create_user(), employes=employes)
        # Création des tâches qui matchent pour la semaine
        total = 0
        total_jour = {}
        if numero_semaine is not None:
            for day in range(1, 8):
                for employe in ferme.employes.all():
                    date = datetime.date.fromisocalendar(annee, numero_semaine, day)
                    total_for_date = self._create_taches(date=date, ferme=ferme, user_tache=employe)
                    if user_concerned.id == employe.id:
                        total += total_for_date
                        total_jour[date.strftime("%d/%m/%Y")] = total_for_date
        if numero_mois is not None:
            _, nb_jours = calendar.monthrange(annee, numero_mois)
            for day in range(1, nb_jours + 1):
                for employe in ferme.employes.all():
                    date = datetime.date(annee, numero_mois, day)
                    total_for_date = self._create_taches(date=date, ferme=ferme, user_tache=employe)
                    if user_concerned.id == employe.id:
                        total += total_for_date
                        total_jour[date.strftime("%d/%m/%Y")] = total_for_date
        return total, total_jour

    def _get_calendrier(self, annee: int, numero_semaine: int = None, numero_mois: int = None, user_id: int = None,
                        expected_status_code=status.HTTP_200_OK):
        if user_id is None:
            user_id = self.get_current_user().id
        query_params = {
            "annee": annee,
            "user_id": user_id
        }
        if numero_semaine is not None:
            query_params['semaine'] = numero_semaine
        if numero_mois is not None:
            query_params['mois'] = numero_mois
        if user_id is not None:
            query_params['user_id'] = user_id
        response = self.client.get(self.url, query_params, headers=self.get_jwt_headers())
        self.assertEqual(response.status_code, expected_status_code)
        return response

    def _check_response(self, response, total: int, total_jour: {}, expected_days: List[str]):
        response_data = json.loads(response.content)
        self.assertEqual(total, response_data.get("total"))
        for expected_day in expected_days:
            expected_total = total_jour.get(expected_day)
            actual_day = next(
                (jour for jour in response_data.get("jours") if jour.get("jour") == expected_day),
                None)
            self.assertIsNotNone(actual_day)
            self.assertEqual(expected_total, actual_day.get("total_jour"))

    def test_calendrier_semaine(self):
        numero_semaine = 3
        total, total_jour = self._create_data(user_concerned=self.init_current_user(), annee=2025, numero_semaine=numero_semaine)
        response = self._get_calendrier(annee=2025, numero_semaine=numero_semaine)
        expected_days = ["13/01/2025", "14/01/2025", "15/01/2025", "16/01/2025", "17/01/2025", "18/01/2025",
                         "19/01/2025"]
        self._check_response(response, total, total_jour, expected_days)

    def test_calendrier_mois(self):
        numero_mois = 2
        total, total_jour = self._create_data(user_concerned=self.init_current_user(), annee=2025, numero_mois=numero_mois)
        response = self._get_calendrier(annee=2025, numero_mois=numero_mois)
        expected_days = ['01/02/2025', '02/02/2025', '03/02/2025', '04/02/2025', '05/02/2025', '06/02/2025',
                         '07/02/2025', '08/02/2025', '09/02/2025', '10/02/2025', '11/02/2025', '12/02/2025',
                         '13/02/2025', '14/02/2025', '15/02/2025', '16/02/2025', '17/02/2025', '18/02/2025',
                         '19/02/2025', '20/02/2025', '21/02/2025', '22/02/2025', '23/02/2025', '24/02/2025',
                         '25/02/2025', '26/02/2025', '27/02/2025', '28/02/2025']
        self._check_response(response, total, total_jour, expected_days)

    def test_calendrier_semaine_specific_user(self):
        responsable = self.init_current_user()
        employe1 = test_fixtures.create_user()
        employes = [employe1, test_fixtures.create_user()]
        ferme = test_fixtures.create_ferme(responsable=responsable, employes=employes)
        numero_semaine = 3
        total, total_jour = self._create_data(numero_semaine=numero_semaine, annee=2025, ferme=ferme, user_concerned=employe1)
        response = self._get_calendrier(annee=2025, numero_semaine=numero_semaine, user_id=employe1.id)
        expected_days = ["13/01/2025", "14/01/2025", "15/01/2025", "16/01/2025", "17/01/2025", "18/01/2025",
                         "19/01/2025"]
        self._check_response(response, total, total_jour, expected_days)

    def test_calendrier_mois_specific_user(self):
        responsable = test_fixtures.create_user()
        employe1 = self.init_current_user()
        employe2 = test_fixtures.create_user()
        employes = [employe1, employe2]
        ferme = test_fixtures.create_ferme(responsable=responsable, employes=employes)
        numero_mois = 2
        total, total_jour = self._create_data(annee=2025, numero_mois=numero_mois, ferme=ferme, user_concerned=employe2)
        response = self._get_calendrier(annee=2025, numero_mois=numero_mois, user_id=employe2.id)
        expected_days = ['01/02/2025', '02/02/2025', '03/02/2025', '04/02/2025', '05/02/2025', '06/02/2025',
                         '07/02/2025', '08/02/2025', '09/02/2025', '10/02/2025', '11/02/2025', '12/02/2025',
                         '13/02/2025', '14/02/2025', '15/02/2025', '16/02/2025', '17/02/2025', '18/02/2025',
                         '19/02/2025', '20/02/2025', '21/02/2025', '22/02/2025', '23/02/2025', '24/02/2025',
                         '25/02/2025', '26/02/2025', '27/02/2025', '28/02/2025']
        self._check_response(response, total, total_jour, expected_days)
