from enum import Enum


class StatutTotal(Enum):
    OK = "Informations complètes"
    WARNING = "Quelques informations manquantes"
    DANGER = "Beaucoup d'informations manquantes"