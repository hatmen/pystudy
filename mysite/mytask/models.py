# -*- coding: utf-8 -*-
from django.db import models

class task(models.Model):
    xlsname = models.CharField(null=False,max_length=50,verbose_name='文件名称')
    topline = models.CharField(blank=True,max_length=250,verbose_name='首行格式')
    tasksql = models.TextField(null=False,max_length=1000,verbose_name='执行语句')
    taskemail = models.CharField(max_length=250,verbose_name='收件人')
    emailsub =  models.CharField(max_length=60,verbose_name='邮件主题')
    emailcon = models.TextField(max_length=100,verbose_name='邮件内容')
    crontime = models.CharField(null=False,max_length=25,verbose_name='任务时间')
    interstat = models.BooleanField(default=True,verbose_name='ON/OFF')
    createtime = models.DateTimeField(verbose_name='创建时间')

    def __unicode__(self):
        return self.xlsname
    
    class Meta:
        db_table = 'mytask_task'
        verbose_name_plural = '运营任务'
        verbose_name = '任务计划'
