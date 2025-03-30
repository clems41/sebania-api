from django.db import models

from base.models import User
from base.models.base import BaseModel


# Create your models here.
class MethodeAgricole(models.Model):
    nom = models.CharField(max_length=50)
    label = models.CharField(max_length=15)

class Ferme(BaseModel):
    nom = models.CharField(max_length=50)
    adresse = models.CharField(max_length=100)
    superficie_cultivee = models.FloatField()
    methodes = models.ManyToManyField(MethodeAgricole)
    responsable = models.OneToOneField(User, on_delete=models.DO_NOTHING, related_name='responsable')
    employes = models.ManyToManyField(User, related_name='employes')