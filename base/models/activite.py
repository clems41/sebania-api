from django.db import models

from base.models import User


class Activite(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    default = models.BooleanField(default=False)
    categorie_default = models.CharField(max_length=50, null=True)
    need_culture = models.BooleanField(default=False)

class ActiviteUser(models.Model):
    class Meta:
        db_table = "base_activite_user"
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    categorie = models.CharField(max_length=15)