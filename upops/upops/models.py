# -*- coding:utf-8 -*-
from django.db import models
from datetime import  datetime
from django.contrib.auth.models import AbstractUser


USER_STATUS = (
    (1, u'已启用'),
    (2, u'已禁用'),
)


class UpUser(models.Model):
    name = models.CharField(max_length=80, primary_key=True)
    email = models.CharField(max_length=80)
    ip = models.CharField(max_length=15, blank=True, null=True)
    password = models.CharField(max_length=60, blank=False)
    comment = models.TextField(max_length=128, blank=True, null=True)
    role = models.IntegerField(choices=USER_STATUS, default=1, blank=True, null=True)
    create_time = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return self.name


class AccessUrl(models.Model):
    url = models.CharField(max_length=100, primary_key=True)
    comment = models.CharField(max_length=160, blank=True, null=True)

    def __unicode__(self):
        return self.url


class User(AbstractUser):
    url = models.ManyToManyField(AccessUrl, blank=True, null=True)

    def __unicode__(self):
        return self.username
