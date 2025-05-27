from django.db import models

class Unite(models.Model):
    nom = models.CharField(max_length=30)