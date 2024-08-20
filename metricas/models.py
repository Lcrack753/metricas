from django.db import models

# Create your models here.
class Response(models.Model):
    service = models.TextField(null=False,blank=False)
    response = models.JSONField(null=False,blank=False)
    params = models.JSONField(null=False,blank=False)
    date = models.DateTimeField(auto_now_add=True, null=False,blank=False)