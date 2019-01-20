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
from boilerplate.settings import *

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
    activation_string = models.CharField(max_length=1000,blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # holds django.utils.timezone.now()
    activation_requested_at = models.DateTimeField()
    email_sent = models.BooleanField(default=False)
    
    def is_valid(self, key):
        
        if (timezone.now() - self.activation_requested_at).total_seconds() > REGISTRATION_ACTIVATION_TIMEOUT :
            return False;
        
        if key != self.activation_string:
            return False;
        
        return True

class PasswordResetRequest(models.Model):
    activation_string = models.CharField(max_length=1000, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # holds django.utils.timezone.now()
    activation_requested_at = models.DateTimeField()
    email_sent = models.BooleanField(default=False)
    already_used = models.BooleanField(default=False)

    def is_not_old(self):
        if self.already_used:
            return False;

        if (timezone.now() - self.activation_requested_at).total_seconds() > PASSWORD_RESET_REQUEST_ACTIVE_TIMEOUT:
            return False;
        else:
            return True;

    def is_valid(self, key):

        if (timezone.now() - self.activation_requested_at).total_seconds() > PASSWORD_RESET_REQUEST_ACTIVE_TIMEOUT:
            return False;

        if key != self.activation_string:
            return False;

        if self.already_used:
            return False;

        return True
        
         
        
      