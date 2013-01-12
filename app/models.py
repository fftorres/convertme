# -*- coding: utf-8 -*-
from django.db import models

class Video(models.Model):
    file = models.FileField(upload_to='videos/%Y/%m/%d')
    job_id = models.IntegerField(default=0, null=True, blank=True)
    job_done = models.BooleanField(default=False)
    
    def __unicode__(self):
        return "Video %s" % self.job_id