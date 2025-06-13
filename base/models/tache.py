from django.db import models

from base.models import Activite, User, Ferme, Parcelle, Culture
from base.models.base import BaseModel
from base.models.unite import Unite
from base.models.vocal import Vocal


class CultureTache(models.Model):
    culture = models.ForeignKey(Culture, on_delete=models.CASCADE)
    quantite = models.FloatField(null=True, blank=True)
    unite = models.ForeignKey(Unite, on_delete=models.DO_NOTHING, null=True)
    nature = models.TextField(null=True, blank=True)
    parcelles = models.ManyToManyField(Parcelle)

    def get_fields_are_missing(self, niveau_complexite: int) -> bool:
        if self.culture.id is None:
            return True
        match niveau_complexite:
            case 1, 2, 3, 4, 5:
                return False
            case 6:
                return self.quantite is None or self.quantite == 0
            case 7:
                return self.parcelles is None or self.parcelles.count() == 0
            case 8:
                return (self.quantite is None or self.quantite == 0) & (
                        self.parcelles is None or self.parcelles.count() == 0
                )
            case _:
                return False


class Tache(BaseModel):
    ferme = models.ForeignKey(Ferme, on_delete=models.CASCADE)
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE)
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    duree_minutes = models.IntegerField()
    cultures = models.ManyToManyField(CultureTache)
    commentaire = models.TextField(null=True, blank=True)
    vocal = models.ForeignKey(Vocal, on_delete=models.DO_NOTHING, null=True)
    quantite = models.FloatField(null=True, blank=True)
    unite = models.ForeignKey(Unite, on_delete=models.DO_NOTHING, null=True)
    nature = models.TextField(null=True, blank=True)
    parcelles = models.ManyToManyField(Parcelle)

    def get_fields_are_missing(self) -> bool:
        if self.duree_minutes <= 0:
            return True
        match self.activite.niveau_complexite:
            case 1:
                return False
            case 2:
                return self.quantite is None or self.quantite == 0
            case 3:
                return self.parcelles.count() == 0
            case 4:
                return self.quantite is None or self.quantite == 0 or self.parcelles.count() == 0
            case 5:
                return self.cultures.count() == 0
            case 6:
                return self.cultures.count() == 0 or self._quantite_is_missing_in_at_least_one_culture()
            case 7:
                return self.cultures.count() == 0 or self._parcelles_is_missing_in_at_least_one_culture()
            case 8:
                return (self.cultures.count() == 0 or self._quantite_is_missing_in_at_least_one_culture() or
                        self._parcelles_is_missing_in_at_least_one_culture())
            case _:
                return False

    def _quantite_is_missing_in_at_least_one_culture(self) -> bool:
        for culture_tache in self.cultures.all():
            if culture_tache.quantite is None or culture_tache.quantite == 0 or culture_tache.unite is None:
                return True
        return False

    def _parcelles_is_missing_in_at_least_one_culture(self) -> bool:
        for culture_tache in self.cultures.all():
            if culture_tache.parcelles.count() == 0:
                return True
        return False
