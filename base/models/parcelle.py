from django.db import models

from base.models import User
from base.models.base import BaseModel


class TypeParcelle(models.Model):
    nom = models.CharField(max_length=20)

# Create your models here.
class Parcelle(BaseModel):
    nom = models.CharField(max_length=20)
    superficie = models.FloatField()
    type = models.ForeignKey(TypeParcelle, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
