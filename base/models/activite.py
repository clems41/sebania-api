from enum import Enum

from django.db import models

from base.models import Ferme

class Activite(models.Model):
    nom = models.CharField(max_length=120, unique=True)
    default = models.BooleanField(default=False)
    categorie_default = models.CharField(max_length=30, null=True)
    mots_cles = models.TextField()
    niveau_complexite = models.IntegerField(default=1)

class ActiviteFerme(models.Model):
    class Meta:
        db_table = "base_activite_ferme"
    activite = models.ForeignKey(Activite, on_delete=models.DO_NOTHING)
    ferme = models.ForeignKey(Ferme, on_delete=models.DO_NOTHING)
    categorie = models.CharField(max_length=30)