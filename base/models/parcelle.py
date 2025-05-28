from django.db import models

from base.models import User, Ferme
from base.models.base import BaseModel


class TypeParcelle(models.Model):
    nom = models.CharField(max_length=40)

# Create your models here.
class Parcelle(BaseModel):
    nom = models.CharField(max_length=80)
    longueur = models.FloatField(null=True)
    largeur = models.FloatField(null=True)
    superficie = models.FloatField(null=True)
    largeur_planche = models.FloatField(null=True, blank=True)
    largeur_passe_pieds = models.FloatField(null=True, blank=True)
    nombre_planches = models.IntegerField(null=True, blank=True)
    type = models.ForeignKey(TypeParcelle, on_delete=models.CASCADE, null=True)
    ferme = models.ForeignKey(Ferme, on_delete=models.CASCADE)
