from django.db import models

from base.models import Ferme


class Culture(models.Model):
    nom = models.CharField(max_length=60, unique=True)
    default = models.BooleanField(default=False)
    categorie_default = models.CharField(max_length=30, null=True)

class CultureFerme(models.Model):
    class Meta:
        db_table = "base_culture_ferme"
    culture = models.ForeignKey(Culture, on_delete=models.DO_NOTHING)
    ferme = models.ForeignKey(Ferme, on_delete=models.DO_NOTHING)
    categorie = models.CharField(max_length=30)