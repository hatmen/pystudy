from django.db import models

class map(models.Model):
    username = models.CharField(max_length=20, blank=False)
    interior_url = models.CharField(max_length=50, blank=False)
    external_url = models.CharField(max_length=50, blank=False)
    create_time = models.DateTimeField()
    
    def __unicode__(self):
        return self.username

