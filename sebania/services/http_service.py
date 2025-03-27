from django.contrib.auth.models import Group

from base.models import Ferme
from sebania.exceptions.auth import UserMustBeAuthenticated
from sebania.exceptions.ferme import FermeNotFoundForUserException


def get_ferme_for_user(request) -> Ferme:
    """
    Retourne la ferme associée à l'utilisateur, qu'il soit responsable ou employés
    """
    if request.user is None or not request.user.is_authenticated:
        raise UserMustBeAuthenticated()
    if Group.objects.get(name='RESPONSABLE').user_set.filter(id=request.user.id).exists():
        return Ferme.objects.get(responsable=request.user)
    elif Group.objects.get(name='EMPLOYE').user_set.filter(id=request.user.id).exists():
        return Ferme.objects.get(employes__id=request.user.id)
    else:
        raise FermeNotFoundForUserException(request.user.id)
