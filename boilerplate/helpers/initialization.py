'''
Created on Jul 9, 2018

@author: havrila
'''
from boilerplate.models import Logger
from django.contrib.auth.models import Group, User
from boilerplate.settings_secret import *

def initialization():
    
    initialized_log = Logger.objects.filter(log_text='INITIALIZED').first()
    if initialized_log is not None and initialized_log.log_text == 'INITIALIZED':
        return   
    
    '''
    PUT YOUR INITIALIZATION HERE
    '''
   # group admin
    ga = Group(name='system_admins')
    ga.save()   
   
    # local admin creation
    user=User.objects.create_user('admin', password='kreten123')
    user.is_superuser=True
    user.is_staff=True
    user.save()
    user.groups.add(ga)
    user.save()
    
    
    '''
    This will block
    '''
    Logger.info('INITIALIZED')
