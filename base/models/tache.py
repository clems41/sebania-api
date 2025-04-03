from django.db import models

from base.models import Activite, User, Ferme, Parcelle
from base.models.base import BaseModel
from base.models.culture import Culture


class Tache(BaseModel):
    ferme = models.ForeignKey(Ferme, on_delete=models.CASCADE)
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE)
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    duree_minutes = models.IntegerField()
    culture = models.ForeignKey(Culture, on_delete=models.DO_NOTHING, null=True)
    parcelles = models.ManyToManyField(Parcelle)
    quantite_recoltee = models.IntegerField(null=True, blank=True)
    commentaire = models.TextField(null=True, blank=True)