from django.db import models

from base.models import Activite, User, Ferme, Parcelle, Culture
from base.models.base import BaseModel
from base.models.unite import Unite


class Tache(BaseModel):
    ferme = models.ForeignKey(Ferme, on_delete=models.CASCADE)
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE)
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    duree_minutes = models.IntegerField()
    culture = models.ForeignKey(Culture, on_delete=models.DO_NOTHING, null=True)
    parcelles = models.ManyToManyField(Parcelle)
    commentaire = models.TextField(null=True, blank=True)
    quantite = models.FloatField(null=True, blank=True)
    unite = models.ForeignKey(Unite, on_delete=models.DO_NOTHING, null=True)
    nature = models.TextField(null=True, blank=True)

    def get_fields_are_missing(self) -> bool:
        if not self.activite.need_culture:
            return self.duree_minutes >= 0
        else:
            if self.activite_id == 17 and (self.quantite == 0 or self.unite is None) : # cas d'une récolte sans quantité ou sans unité
                return True
            return self.culture is None or len(self.parcelles.all()) == 0
