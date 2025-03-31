from django.db import models

from base.models import User, Ferme
from base.models.base import BaseModel


class TypeParcelle(models.Model):
    nom = models.CharField(max_length=20)

# Create your models here.
class Parcelle(BaseModel):
    nom = models.CharField(max_length=20)
    superficie = models.FloatField()
    type = models.ForeignKey(TypeParcelle, on_delete=models.CASCADE)
    ferme = models.ForeignKey(Ferme, on_delete=models.CASCADE)
