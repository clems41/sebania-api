from django.db import models


class Email(models.Model):
    sender = models.CharField(max_length=30)
    receiver = models.CharField(max_length=30)
    subject = models.CharField(max_length=30)
    content = models.TextField()
    template_name = models.CharField(max_length=30)
    template_context = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    error = models.TextField(null=True, default=None)