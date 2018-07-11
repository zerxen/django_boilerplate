'''
Created on Jul 9, 2018

@author: havrila
'''

'''
HELPER LIBS
'''
import datetime
import re

from django.db import models
from django.utils import timezone;

from django.contrib.auth.models import Group, User
from django.contrib.auth.models import AbstractUser


'''
    DB LOG Class
'''
class Logger(models.Model):
    date = models.DateTimeField('date published')
    log_text = models.CharField(max_length=5000)
    
    OBJECT_TYPES = (
        (0, 'emergencies'),
        (1, 'alerts'),
        (2, 'critical'),
        (3, 'errors'),
        (4, 'warnings'),
        (5, 'notifications'),
        (6, 'informational'),
        (7, 'debugging'),
    )    
    severity = models.PositiveSmallIntegerField(default=6)    

    @staticmethod
    def debug(log_text):
        now = timezone.now()
        log = Logger(date=now,log_text=log_text)
        log.severity = 7
        log.save() 
        print("LOG["+ str(log.severity) + "]: " + log_text)
    
    @staticmethod
    def info(log_text):
        now = timezone.now()
        log = Logger(date=now,log_text=log_text)
        log.save() 
        print("LOG["+ str(log.severity) + "]: " + log_text)
        
    @staticmethod
    def error(log_text):
        now = timezone.now()
        log = Logger(date=now,log_text=log_text)
        log.severity = 3
        log.save() 
        print("ERROR["+ str(log.severity) + "]: " + log_text)        
        
        
class Activation(models.Model):
    activation_string = models.CharField(max_lenght=1024)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # holds django.utils.timezone.now()
    activation_requested_at = models.DateTimeField()
      