from enum import Enum


class StatutTache(Enum):
    OK = "Informations complètes"
    WARNING = "Quelques informations manquantes"
    DANGER = "Beaucoup d'informations manquantes"

    @classmethod
    def from_statuts(cls, statuts: []):
        return cls.from_statut_names(statut.name for statut in statuts)

    @classmethod
    def from_statut_names(cls, names: []):
        worst_statut = StatutTache.OK
        for name in names:
            if name == StatutTache.DANGER.name:
                worst_statut = StatutTache.DANGER
            elif name == StatutTache.WARNING.name and worst_statut != StatutTache.DANGER:
                worst_statut = StatutTache.WARNING
        return worst_statut