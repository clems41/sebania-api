from typing import List

from django.contrib.auth.models import Group

from base.models import User, Ferme, MethodeAgricole
from sebania.services import crypto_service

def create_user() -> User:
    return User.objects.create_user(email=crypto_service.random_email(), password=crypto_service.generate_password(),
                        first_name=crypto_service.random_string(), last_name=crypto_service.random_string())

def create_ferme(responsable: User = None, employes=None) -> Ferme:
    # Création de la ferme
    responsable_group = Group.objects.get(name='RESPONSABLE')
    if responsable is None:
        responsable = create_user()
    if employes is None:
        employes = [create_user(), create_user()]
    responsable_group.user_set.add(responsable)
    nom = crypto_service.random_string()
    adresse = crypto_service.random_string(20, digit=True)
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
    return ferme


