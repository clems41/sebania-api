from typing import List

from django.contrib.auth.models import Group
from django.utils import timezone

from base.models import User, Ferme, MethodeAgricole, Parcelle, Tache
from sebania.utils import crypto_utils

def create_user() -> User:
    return User.objects.create_user(email=crypto_utils.random_email(), password=crypto_utils.generate_password(),
                        first_name=crypto_utils.random_string(), last_name=crypto_utils.random_string())

def create_parcelle(ferme: Ferme) -> Parcelle:
    return Parcelle.objects.create(nom=crypto_utils.random_string(), superficie=120, type_id=1, ferme=ferme)

def create_tache(ferme: Ferme,  user_id: int, nb_parcelles: int = 2) -> Tache:
    tache = Tache.objects.create(ferme=ferme, date=timezone.now(), user_id=user_id, activite_id=3, duree_minutes=90,
                                 culture_id=3, quantite_recoltee=0, commentaire=crypto_utils.random_string(length=150))
    for _ in range(nb_parcelles):
        parcelle = create_parcelle(ferme)
        tache.parcelles.add(parcelle)
    return tache

def create_ferme(responsable: User = None, employes=None, nb_parcelles: int = 0) -> Ferme:
    # Création de la ferme
    responsable_group = Group.objects.get(name='RESPONSABLE')
    if responsable is None:
        responsable = create_user()
    if employes is None:
        employes = [create_user(), create_user()]
    responsable_group.user_set.add(responsable)
    nom = crypto_utils.random_string()
    adresse = crypto_utils.random_string(20, digit=True)
    superficie_cultivee = 1500.0
    ferme = Ferme.objects.create(responsable=responsable, nom=nom, adresse=adresse, superficie_cultivee=superficie_cultivee)

    # Création des employés et ajout à la ferme
    employe_group = Group.objects.get(name='EMPLOYE')
    for employe in employes:
        ferme.employes.add(employe)
        employe_group.user_set.add(employe)

    # Ajout des méthodes
    methode = MethodeAgricole.objects.get(nom__iregex='biologique')
    ferme.methodes.add(methode)

    # Création des parcelles associées
    for _ in range(nb_parcelles):
        create_parcelle(ferme)
    return ferme
