from django.db import models

from base.models import User


class Monitoring(models.Model):
    occurred_at = models.DateTimeField(auto_now_add=True)
    url = models.URLField()
    query_params = models.JSONField()
    body = models.JSONField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    returned_status = models.IntegerField()
