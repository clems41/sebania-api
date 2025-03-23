from django.db import models

from base.models import User, Ferme


class Activite(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    default = models.BooleanField(default=False)
    categorie_default = models.CharField(max_length=50, null=True)
    need_culture = models.BooleanField(default=False)

class ActiviteFerme(models.Model):
    class Meta:
        db_table = "base_activite_ferme"
    activite = models.ForeignKey(Activite, on_delete=models.DO_NOTHING)
    ferme = models.ForeignKey(Ferme, on_delete=models.DO_NOTHING)
    categorie = models.CharField(max_length=15)