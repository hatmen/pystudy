from django.db import models


class TrustHost(models.Model):
    ip = models.CharField(max_length=32, blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    user = models.CharField(max_length=16, blank=True, null=True)
    date_added = models.DateTimeField(auto_now=True, null=True)

    def __unicode__(self):
        return self.ip


class AutoProject(models.Model):
    project_name = models.CharField(max_length=32, blank=True, null=True)
    ip = models.ManyToManyField(TrustHost, blank=True, null=True)
    date_added = models.DateTimeField(auto_now=True, null=True)

    def __unicode__(self):
        return self.project_name

