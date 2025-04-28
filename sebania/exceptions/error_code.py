from enum import Enum
from rest_framework import status


def get_error_code_from_str(value):
    for error_code in ErrorCode:
        if value == error_code.name:
            return error_code
    return None

class ErrorCode(Enum):
    """
    ERREURS GLOBALES
    """
    GLOBAL_UNKNOWN_ERROR = "Une erreur inattendu s'est produite : {}", status.HTTP_500_INTERNAL_SERVER_ERROR
    GLOBAL_VALIDATION_ERROR = "{}", status.HTTP_400_BAD_REQUEST
    GLOBAL_WRONG_ARG = "La méthode {method} ne peut pas être appelée avec un argument de type {actual}, uniquement avec les types suivantes : {must_be}", status.HTTP_500_INTERNAL_SERVER_ERROR
    
    """
    ERREURS AUTHENTIFICATION
    """
    AUTH_USER_MUST_BE_AUTHENTICATED = "L'utilisateur doit être authentifié", status.HTTP_403_FORBIDDEN
    AUTH_USER_EMAIL_MUST_NOT_BE_EMPTY = "Un utilisateur ne peut pas être créé sans adresse email", status.HTTP_400_BAD_REQUEST
    AUTH_EMPLOYE_CANNOT_POST_FOR_RESPONSABLE = "Les employés ne peuvent pas agir pour les responsables ou les autres employés", status.HTTP_403_FORBIDDEN
    
    """
    ERREURS LIEES AUX USER
    """
    USER_NOT_FOUND = "L'utilisateur id={} n'a pas pu être trouvé", status.HTTP_404_NOT_FOUND
    USER_OLD_PASSWORD_INCORRECT = "L'ancien mot de passe ne correspond pas", status.HTTP_403_FORBIDDEN

    """
    ERREURS LIEES AUX CONTACT
    """
    CONTACT_MESSAGE_EMPTY = "Le message ne peut pas être vide", status.HTTP_400_BAD_REQUEST

    """
    ERREURS LIEES A LA FERME
    """
    FERME_NOT_FOUND_FOR_USER = "La ferme n'a pu être trouvée pour l'utilisateur id={}", status.HTTP_404_NOT_FOUND
    FERME_NOT_FOUND = "La ferme id={} n'a pu être trouvée", status.HTTP_404_NOT_FOUND

    """
    ERREURS LIEES AUX PARCELLES
    """
    PARCELLE_TYPE_NOT_FOUND = "Le type parcelle id={} n'a pu être trouvé", status.HTTP_404_NOT_FOUND
    PARCELLE_NOT_FOUND = "La parcelle id={} n'a pu être trouvée pour la ferme concernée", status.HTTP_404_NOT_FOUND
    PARCELLE_SUPERFICIE_INCORRECT = "La superficie doit être supérieure à 0", status.HTTP_400_BAD_REQUEST
    PARCELLE_NOM_DEJA_EXISTANT = "Le nom={} de parcelle est déjà utilisée", status.HTTP_400_BAD_REQUEST
    
    """
    ERREURS LIEES AUX ACTIVITES
    """
    ACTIVITE_NOT_FOUND = "L'activité id={} n'a pas pu être trouvé", status.HTTP_404_NOT_FOUND
    ACTIVITE_QUERY_TOO_SHORT = "Le paramètre 'query' doit au moins contenir 3 caractères, or il en contient {}", status.HTTP_400_BAD_REQUEST
    
    """
    ERREURS LIEES AUX CULTURES
    """
    CULTURE_NOT_FOUND = "La culture id={} n'a pas pu être trouvée", status.HTTP_404_NOT_FOUND

    """
    ERREURS LIEES AUX TACHES
    """
    TACHE_CALENDRIER_FILTRE_INCORRECT = "Vous devez filtrer soit par mois, soit par semaine, pas les 2 ou aucun, or semaine={semaine} et mois={mois}", status.HTTP_400_BAD_REQUEST
    TACHE_CALENDRIER_ANNEE_OBLIGATOIRE = "Le filtre année est obligatoire", status.HTTP_400_BAD_REQUEST
    TACHE_CALENDRIER_USERID_OBLIGATOIRE = "Le filtre user_id est obligatoire", status.HTTP_400_BAD_REQUEST
    TACHE_DUREE_INCORRECTE = "La durée de la tâche ({}) doit être comprise entre 1 et 1440", status.HTTP_400_BAD_REQUEST

    """
    ERREURS LIEES AUX VOCAUX
    """
    VOCAL_FILE_UPLOAD = "Erreur lors de la récupération du message vocal depuis la requête : {}", status.HTTP_400_BAD_REQUEST
    VOCAL_DATE_INCORRECTE = "La date fournie ({}) est incorrecte, elle doit être au format ddMMYYYY", status.HTTP_400_BAD_REQUEST