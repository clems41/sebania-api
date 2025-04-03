from django.db import models

from base.models import Ferme


class Activite(models.Model):
    nom = models.CharField(max_length=120, unique=True)
    default = models.BooleanField(default=False)
    categorie_default = models.CharField(max_length=30, null=True)
    need_culture = models.BooleanField(default=False)

class ActiviteFerme(models.Model):
    class Meta:
        db_table = "base_activite_ferme"
    activite = models.ForeignKey(Activite, on_delete=models.DO_NOTHING)
    ferme = models.ForeignKey(Ferme, on_delete=models.DO_NOTHING)
    categorie = models.CharField(max_length=30)