from django.db import models

from base.models import Ferme
from base.models.base import BaseModel
from sebania.utils.serializer_utils import is_not_zero, is_zero


class TypeParcelle(models.Model):
    nom = models.CharField(max_length=40)

# Create your models here.
class Parcelle(BaseModel):
    nom = models.CharField(max_length=80)
    longueur = models.FloatField(null=True)
    largeur = models.FloatField(null=True)
    superficie = models.FloatField(null=True)
    superficie_cultivee = models.FloatField(null=True)
    largeur_planche = models.FloatField(null=True, blank=True)
    largeur_passe_pieds = models.FloatField(null=True, blank=True)
    nombre_planches = models.IntegerField(null=True, blank=True)
    type = models.ForeignKey(TypeParcelle, on_delete=models.CASCADE, null=True)
    ferme = models.ForeignKey(Ferme, on_delete=models.CASCADE)
    
    def fill_empty_fields(self, all_fields: bool = False):
        if all_fields:
            self._fill_longueur()
            self._fill_largeur()
            self._fill_largeur_planche()
            self._fill_nombre_planches()
        self._fill_largeur_passe_pieds()
        self._fill_superficie()
        self._fill_superficie_cultivee()
        self.save()

    def _fill_longueur(self):
        if is_zero(self.longueur):
            if is_not_zero(self.largeur) and is_not_zero(self.superficie):
                self.longueur = self.superficie / self.largeur

    def _fill_largeur(self):
        if is_zero(self.largeur):
            if is_not_zero(self.longueur) and is_not_zero(self.superficie):
                self.largeur = round(self.superficie / self.longueur, 3)
            if is_not_zero(self.largeur_planche) and is_not_zero(self.largeur_passe_pieds) and is_not_zero(self.nombre_planches):
                self.largeur = (self.largeur_planche + self.largeur_passe_pieds) * self.nombre_planches

    def _fill_largeur_planche(self):
        if is_zero(self.largeur_planche):
            if is_not_zero(self.largeur) and is_not_zero(self.largeur_passe_pieds) and is_not_zero(self.nombre_planches):
                self.largeur_planche = round((self.largeur / self.nombre_planches) - self.largeur_passe_pieds, 3)

    def _fill_nombre_planches(self):
        if is_zero(self.nombre_planches):
            if is_not_zero(self.largeur_planche) and is_not_zero(self.largeur) and is_not_zero(self.largeur_passe_pieds):
                self.nombre_planches = round(self.largeur / (self.largeur_planche + self.largeur_passe_pieds), 3)

    def _fill_largeur_passe_pieds(self):
        if is_not_zero(self.largeur_planche) and is_not_zero(self.largeur) and is_not_zero(self.nombre_planches):
            self.largeur_passe_pieds = round((self.largeur / self.nombre_planches) - self.largeur_planche, 3)

    def _fill_superficie(self):
        if is_not_zero(self.longueur) and is_not_zero(self.largeur):
            self.superficie = self.longueur * self.largeur

    def _fill_superficie_cultivee(self):
        if is_not_zero(self.longueur) and is_not_zero(self.largeur_planche) and is_not_zero(self.nombre_planches):
            self.superficie_cultivee = self.longueur * self.largeur_planche * self.nombre_planches
