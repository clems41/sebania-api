from enum import Enum


class StatutTache(Enum):
    OK = "Informations complètes"
    WARNING = "Quelques informations manquantes"
    DANGER = "Beaucoup d'informations manquantes"