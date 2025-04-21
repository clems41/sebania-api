from enum import Enum


class ErrorCode(Enum):
    """
    ERREURS GLOBALES
    """
    GLOBAL_UNKNOWN_ERROR = "unknown_error"
    GLOBAL_WRONG_ARG = "wrong_arg_for_method"
    
    """
    ERREURS AUTHENTIFICATION
    """
    AUTH_USER_MUST_BE_AUTHENTICATED = "user_must_be_authenticated"
    AUTH_EMPLOYE_CANNOT_POST_FOR_RESPONSABLE = "employe_cannot_post_for_responsable"
    
    """
    ERREURS LIEES AUX USER
    """
    USER_NOT_FOUND = "user_not_found"
    """
    ERREURS LIEES A LA FERME
    """
    FERME_NOT_FOUND_FOR_USER = "ferme_not_found_for_user"
    FERME_NOT_FOUND = "ferme_not_found"
    """
    ERREURS LIEES AUX PARCELLES
    """
    PARCELLE_TYPE_NOT_FOUND = "parcelle_type_not_found"
    PARCELLE_NOT_FOUND = "parcelle_not_found"
    
    """
    ERREURS LIEES AUX ACTIVITES
    """
    ACTIVITE_NOT_FOUND = "activite_not_found"
    ACTIVITE_QUERY_TOO_SHORT = "activite_query_too_short"
    
    """
    ERREURS LIEES AUX CULTURES
    """
    CULTURE_NOT_FOUND = "culture_not_found"