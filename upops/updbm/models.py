# -*- coding:utf-8 -*-
from django.db import models
from upops.models import UpUser
from datetime import datetime

DBM_STATUS = (
    (1, u'待审核'),
    (2, u'已通过'),
    (3, u'已驳回'),
)


class DBManage(models.Model):
    username = models.ForeignKey(UpUser, blank=False)
    use_ip = models.CharField(max_length=16, blank=False)
    use_db = models.CharField(max_length=50, blank=False)
    authorization = models.CharField(max_length=120, blank=True, null=True)
    create_time = models.DateTimeField(default=datetime.now)
    comment = models.TextField(max_length=128, blank=True, null=True)
    status = models.IntegerField(choices=DBM_STATUS,  blank=True, null=True)

    def __unicode__(self):
        return self.username


class DbImportTest(models.Model):
    testdb = models.CharField(max_length=50, blank=True, null=True)
    backdb = models.CharField(max_length=50, blank=True, null=True)
    create_time = models.DateTimeField(default=datetime.now)
    counter = models.CharField(max_length=16, blank=True, null=True)
    table_sum = models.CharField(max_length=16, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)

    def __unicode__(self):
        return self.testdb


class DbLifeTime(models.Model):
    username = models.ForeignKey(UpUser, blank=False)
    use_ip = models.CharField(max_length=16, blank=False)
    use_db = models.CharField(max_length=50, blank=False)
    life_time = models.CharField(max_length=20, blank=False)

    def __unicode__(self):
        return self.username
