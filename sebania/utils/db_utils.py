from django.contrib.auth.models import Group
from django.utils import timezone

from base.models import Ferme, User
from sebania.exceptions.auth import UserMustBeAuthenticatedException
from sebania.exceptions.common import WrongArgForMethodException
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.ferme import FermeNotFoundForUserException
from sebania.utils import crypto_utils


def soft_delete_employe(user_id: int):
    """
    Modifie les données d'un utilisateur existant pour qu'il ne puisse plus accéder à l'application mais qu'il puisse toujours se créer un nouveau compte en utilisant la même adresse email
    """
    user = User.objects.get(id=user_id)
    anonymous_username = "delete_" + user.email + "_" + crypto_utils.random_email()
    user.email = anonymous_username
    user.username = anonymous_username
    user.is_active = False
    user.deleted_at = timezone.now()
    user.save()

def user_is_responsable(user_id : int):
    return Group.objects.get(name='RESPONSABLE').user_set.filter(id=user_id).exists()

def user_is_employe(user_id : int):
    return Group.objects.get(name='EMPLOYE').user_set.filter(id=user_id).exists()

def get_ferme_for_user(request) -> Ferme:
    """
    Retourne la ferme associée à l'utilisateur, qu'il soit responsable ou employés
    """
    if request.user is None or not request.user.is_authenticated:
        raise UserMustBeAuthenticatedException()
    if user_is_responsable(request.user.id):
        return Ferme.objects.get(responsable=request.user)
    elif user_is_employe(request.user.id):
        return Ferme.objects.get(employes__id=request.user.id)
    else:
        raise FermeNotFoundForUserException(request.user.id)

def get_one_or_raise_exception(queryset, exception: CustomException, *filter_args, **filter_kwargs):
    """
    Retourne l'instance de l'objet demandé si elle existe, sinon lève une exception
    """
    if hasattr(queryset, "_default_manager"):
        queryset = queryset._default_manager.all()
    if not hasattr(queryset, "get"):
        klass__name = (
            queryset.__name__ if isinstance(queryset, type) else queryset.__class__.__name__
        )
        raise WrongArgForMethodException(method="get_one_or_raise_exception", actual=klass__name, must_be="Model, Manager or QuerySet")
    try:
        return queryset.get(*filter_args, **filter_kwargs)
    except queryset.model.DoesNotExist:
        raise exception



