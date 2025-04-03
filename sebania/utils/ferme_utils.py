from base.models import Ferme, User


def user_is_in_ferme(user: User, ferme: Ferme) -> bool:
    return ferme.responsable.id == user.id or user.id in [employe.id for employe in ferme.employes.all()]