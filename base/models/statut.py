from enum import Enum


class StatutJour(Enum):
    OK = "Nombre d'heures inférieures ou égales à 9"
    WARNING = "Nombre d'heures inférieures ou égales à 10"
    DANGER = "Nombre d'heures supérieures à 10"

    @classmethod
    def from_total_jour(cls, total_jour_minutes: int):
        if total_jour_minutes / 60 <= 9: return cls.OK
        elif total_jour_minutes / 60 <= 10: return cls.WARNING
        else: return cls.DANGER