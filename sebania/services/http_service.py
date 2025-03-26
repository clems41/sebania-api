from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied

from base.models import Ferme


def get_ferme_for_user(request) -> Ferme:
    if request.user is None or not request.user.is_authenticated:
        raise PermissionDenied("Impossible de récupérer la ferme associée car l'utilisateur n'est pas authentifié")
    if Group.objects.get(name='RESPONSABLE').user_set.filter(id=request.user.id).exists():
        return Ferme.objects.get(responsable=request.user)
    elif Group.objects.get(name='EMPLOYE').user_set.filter(id=request.user.id).exists():
        return Ferme.objects.get(employes__id=request.user.id)
    else:
        raise PermissionDenied("Impossible de récupérer la ferme associée car l'utilisateur n'est ni responsable, ni employé")
