from django.db import models

from base.models import Activite, User, Ferme, Parcelle, Culture
from base.models.base import BaseModel
from base.models.statut import StatutTache
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

    def get_statut(self) -> StatutTache:
        if not self.activite.need_culture:
            return StatutTache.OK
        nb_point = 0
        if self.culture:
            nb_point += 1
        if self.parcelles and len(self.parcelles.all()) > 0:
            nb_point += 1
        statut = StatutTache.DANGER
        if nb_point == 1:
            statut = StatutTache.WARNING
        if nb_point == 2:
            statut = StatutTache.OK
        return statut
