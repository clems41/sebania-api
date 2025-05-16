from django.contrib.auth.models import Group
from django.utils import timezone

from base.models import Ferme, User
from sebania.exceptions.custom_exception import CustomException
from sebania.exceptions.error_code import ErrorCode
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

def get_ferme_from_request(request) -> Ferme:
    """
    Retourne la ferme associée à l'utilisateur, qu'il soit responsable ou employés
    """
    if request.user is None or not request.user.is_authenticated:
        raise CustomException(ErrorCode.USER_MUST_BE_AUTHENTICATED)
    return get_ferme_for_user(request.user.id)

def get_ferme_for_user(user_id: int) -> Ferme:
    """
    Retourne la ferme associée à l'utilisateur, qu'il soit responsable ou employés
    """
    if user_is_responsable(user_id):
        return Ferme.objects.get(responsable_id=user_id)
    elif user_is_employe(user_id):
        return Ferme.objects.get(employes__id=user_id)
    else:
        raise CustomException(ErrorCode.FERME_NOT_FOUND_FOR_USER, user_id)

def get_one_or_raise_exception(queryset, exception: CustomException, defer_fields: list = None, *filter_args, **filter_kwargs):
    """
    Retourne l'instance de l'objet demandé si elle existe, sinon lève une exception
    """
    if hasattr(queryset, "_default_manager"):
        queryset = queryset._default_manager.all()
    if not hasattr(queryset, "get"):
        klass__name = (
            queryset.__name__ if isinstance(queryset, type) else queryset.__class__.__name__
        )
        raise CustomException(ErrorCode.GLOBAL_WRONG_ARG, method="get_one_or_raise_exception", actual=klass__name, must_be="Model, Manager or QuerySet")
    try:
        if defer_fields:
            queryset = queryset.defer(*defer_fields)
        return queryset.get(*filter_args, **filter_kwargs)
    except queryset.model.DoesNotExist:
        raise exception

def get_one_or_none(queryset, defer_fields: list = None, *filter_args, **filter_kwargs):
    """
    Retourne l'instance de l'objet demandé si elle existe, sinon None
    """
    if hasattr(queryset, "_default_manager"):
        queryset = queryset._default_manager.all()
    if not hasattr(queryset, "get"):
        klass__name = (
            queryset.__name__ if isinstance(queryset, type) else queryset.__class__.__name__
        )
        raise CustomException(ErrorCode.GLOBAL_WRONG_ARG, method="get_one_or_none", actual=klass__name, must_be="Model, Manager or QuerySet")
    try:
        if defer_fields:
            queryset = queryset.defer(*defer_fields)
        return queryset.get(*filter_args, **filter_kwargs)
    except queryset.model.DoesNotExist:
        return None
