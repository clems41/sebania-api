from django.db import models

from base.models import User


class Unite(models.Model):
    nom = models.CharField(max_length=30)
    label = models.CharField(max_length=2)

class Culture(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    unite = models.ForeignKey(Unite, on_delete=models.CASCADE)
    default = models.BooleanField(default=False)
    categorie_default = models.CharField(max_length=50, null=True)

class CultureUser(models.Model):
    class Meta:
        db_table = "base_culture_user"
    culture = models.ForeignKey(Culture, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    categorie = models.CharField(max_length=15)