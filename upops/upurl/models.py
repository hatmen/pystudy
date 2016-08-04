from django.db import models
from datetime import datetime
# Create your models here.


class UrlGroup(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)
    comment = models.TextField(max_length=128, blank=True, null=True)

    def __unicode__(self):
        return self.name


class Url(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)
    http = models.TextField(max_length=128, blank=True, null=True)
    info = models.CharField(max_length=128, blank=True, null=True)
    group = models.ForeignKey(UrlGroup, blank=True, null=True, on_delete=models.SET_NULL)
    comment = models.TextField(max_length=128, blank=True, null=True)
    create_time = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return self.name
