from django.db import models


class dbname_info(models.Model):
    username = models.CharField(max_length=50, blank=False)
    use_ip = models.CharField(max_length=16, blank=False)
    use_db = models.CharField(max_length=50, blank=False)
    authorization = models.TextField()
    create_time = models.DateTimeField()

class dbuser_info(models.Model):
    username = models.CharField(max_length=50, blank=False)
    use_ip = models.CharField(max_length=16, blank=False)
    passwd = models.CharField(max_length=60, blank=False)

class task_info(models.Model):
    only_id = models.CharField(max_length=8, blank=False, unique=True)
    file_name = models.CharField(max_length=50, blank=False)
    task_email = models.CharField(max_length=100, blank=False)
    email_subject = models.CharField(max_length=60, blank=False)
    email_context = models.TextField()
    email_crontab = models.CharField(max_length=25, blank=False)
    task_status = models.BooleanField(default=True)
    create_time = models.DateTimeField()

class task_content(models.Model):
    only_id = models.CharField(max_length=8, blank=False)
    sheet_name = models.CharField(max_length=50, blank=False)
    task_sql = models.TextField()
    top_line = models.CharField(max_length=50, blank=False)
    create_time = models.DateTimeField()

class mapping(models.Model):
    username = models.CharField(max_length=20, blank=False)
    interior_url = models.CharField(max_length=50, blank=False)
    external_url = models.CharField(max_length=50, blank=False)
    create_time = models.DateTimeField()
