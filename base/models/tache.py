from django.db import models

from base.models import Activite, User, Ferme, Parcelle, Culture
from base.models.base import BaseModel
from base.models.unite import Unite
from base.models.vocal import Vocal


class CultureTache(models.Model):
    culture = models.ForeignKey(Culture, on_delete=models.CASCADE)
    quantite = models.FloatField(null=True, blank=True)
    unite = models.ForeignKey(Unite, on_delete=models.DO_NOTHING, null=True)
    nature = models.TextField(null=True, blank=True)
    parcelles = models.ManyToManyField(Parcelle)

class Tache(BaseModel):
    ferme = models.ForeignKey(Ferme, on_delete=models.CASCADE)
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE)
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    duree_minutes = models.IntegerField()
    cultures = models.ManyToManyField(CultureTache)
    commentaire = models.TextField(null=True, blank=True)
    vocal = models.ForeignKey(Vocal, on_delete=models.DO_NOTHING, null=True)
    quantite = models.FloatField(null=True, blank=True)
    unite = models.ForeignKey(Unite, on_delete=models.DO_NOTHING, null=True)
    nature = models.TextField(null=True, blank=True)
    parcelles = models.ManyToManyField(Parcelle)

    def get_fields_are_missing(self) -> bool:
        if not self.activite.need_culture:
            return self.duree_minutes >= 0
        elif self.cultures.count() == 0:
            return True
        else:
            for culture_tache in self.cultures.all():
                if self.activite_id == 17:
                    if culture_tache.quantite == 0 or culture_tache.unite is None:
                        # cas d'une récolte sans quantité ou sans unité pour au moins une des cultures : return True
                        return True
                else:
                    if culture_tache.parcelles.count() == 0:
                        # cas d'une saisie de culture sans préciser la parcelle : return True
                        return True
            return False