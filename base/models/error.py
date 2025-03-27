from django.db import models

from base.models import User

class Error(models.Model):
    message = models.TextField()
    traceback = models.TextField()
    url = models.URLField()
    query_params = models.JSONField()
    body = models.JSONField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
