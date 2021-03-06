'''
Created on Jul 9, 2018

@author: havrila
'''

from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.template import loader
from django.http import HttpResponse,HttpResponseForbidden
from boilerplate.helpers import initialization
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages;
from django.core.mail import send_mail
from django import forms
from boilerplate.models import *
import boilerplate
import hashlib
import datetime
from django.utils import timezone
from django.core.validators import EmailValidator
import re
from boilerplate.settings_secret import *


class BaseView(TemplateView):
    template_name = "boilerplate/base_template.html"
    model = User
    context_object_name = 'user'
    extra_context = {}
    
    # 
    def get(self, request, *args, **kwargs): 
        
        # JUST IN CASE
        initialization.initialization()
        
        context = {
            self.context_object_name: request.user,
        }         
        context.update(self.extra_context)                
       
        template = loader.get_template(self.template_name)
        return HttpResponse(template.render(context, request))  
    
class LoginView(BaseView):
    template_name = "boilerplate/base_extensions/login.html"
    def post(self, request, *args, **kwargs):
        if request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')         
            
            print("DEBUG: " + username + "/" +  password)
            
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                state = "Valid account"
                if request.POST.get('next') is not None and request.POST.get('next') != '':
                    next = request.POST.get('next')
                else:
                    next = "/"
                #return redirect(reverse(next))
                return redirect(next)
            else:
                messages.add_message(request, messages.ERROR, "Authentication Failed" )     
                HttpResponseForbidden("Invalid account")
        
        # GENERIC RETURN           
        return redirect('index')    
    
class LogoutView(BaseView):
    def get(self, request, *args, **kwargs): 
        logout(request)
        # Redirect to a success page.
        return redirect('index')

class PasswordResetForm(forms.Form):
    email = forms.EmailField()
    password1 = forms.CharField(max_length=64)
    password2 = forms.CharField(max_length=64)
    notes = forms.CharField(required=False)
    key = forms.CharField(max_length=200)

class PasswordResetView(TemplateView):
    template_name = "boilerplate/base_extensions/password_reset.html"
    model = User
    context_object_name = 'user'
    extra_context = {}
    MIN_LENGTH = 8

    '''
    Small function to put error message back to the user
    '''
    def return_error(self, request, error_text):
        messages.add_message(request, messages.ERROR, error_text)
        context = {
        }
        template = loader.get_template(self.template_name)
        return HttpResponse(template.render(context, request))

        #

    def get(self, request, *args, **kwargs):

        if 'key' not in request.GET or not re.match(r"\b[a-f0-9]{128}\b", request.GET.get('key')):
            return self.return_error(request, "Invalid data in request[03]")

        key = request.GET.get('key')
        password_reset_request_obj = PasswordResetRequest.objects.filter(activation_string=key).last()

        if not password_reset_request_obj:
            return self.return_error(request, "Cannot find a valid password reset request based on provided key")

        if not password_reset_request_obj.is_valid(request.GET.get('key')):
            return self.return_error(request, "Request key not valid[04]")

        # reply context to create a pre-filled form for password reset
        context = {
            'valid_reset_request' : "success",
            'email': password_reset_request_obj.user.username,
            'key': key
        }
        context.update(self.extra_context)

        template = loader.get_template(self.template_name)
        return HttpResponse(template.render(context, request))

    '''
    Small function to put error message back to the user
    '''
    def return_error_and_prefill_form(self, request, regform, key, error_text ):
        messages.add_message(request, messages.ERROR, error_text)
        context = {
            'email': regform.data['email'],
            'valid_reset_request': "success",
            'key': key
        }
        template = loader.get_template(self.template_name)
        return HttpResponse(template.render(context, request))

    '''
    validate post entry, create user that is disabled and send email with activation
    '''
    def post(self, request, *args, **kwargs):
        if request.POST:
            regform = PasswordResetForm(request.POST)
            if regform.is_valid():
                Logger.debug(
                    "RegistrationView - VALID input: " + regform.cleaned_data['email'] + " / " + regform.cleaned_data[
                        'password1'] + " / " + regform.cleaned_data['password2'] + " / " + regform.cleaned_data['key'])

            ###
            ### Here we validate if the request (key) is valid
            ###
            password_reset_request_obj = PasswordResetRequest.objects.filter(
                activation_string=regform.cleaned_data['key']).last()
            if not password_reset_request_obj:
                return self.return_error_and_prefill_form(request, regform, regform.cleaned_data['key'],
                                                          "Provided password reset key is not valid! [01]")

            if not password_reset_request_obj.is_valid(regform.cleaned_data['key']):
                return self.return_error_and_prefill_form(request, regform, regform.cleaned_data['key'],
                                                          "Provided password reset key is not valid! [02]")

            ##
            ## VALIDATE INPUT AND ANY ENFORCMENT IF YOU WANT
            ##
            if not regform.is_valid():
                # ERRORS IN FIELDS
                for field in regform.errors:
                    for error_text in regform.errors[field]:
                        messages.add_message(request, messages.ERROR, str(field) + ": " + str(error_text))
                        Logger.debug("PasswordResetForm -" + str(field) + ": " + str(error_text))

                # PREFILL FORM TO FIX
                context = {
                    'email': regform.data['email'],
                    'valid_reset_request': "success",
                    'key': key
                }
                template = loader.get_template(self.template_name)
                return HttpResponse(template.render(context, request))

                ##
            ## Check for password policies
            ##
            if regform.cleaned_data['password1'] != regform.cleaned_data['password2']:
                return self.return_error_and_prefill_form(request, regform, regform.cleaned_data['key'], "Passwords do not match!")

            if len(regform.cleaned_data['password1']) < self.MIN_LENGTH:
                return self.return_error_and_prefill_form(request, regform, regform.cleaned_data['key'],
                                                          "Passwords is shorter than " + str(self.MIN_LENGTH) + "!")

            first_isalpha = regform.cleaned_data['password1'].isalpha()
            if all(c.isalpha() == first_isalpha for c in regform.cleaned_data['password1']):
                return self.return_error_and_prefill_form(request, regform, regform.cleaned_data['key'],
                                                          "Password has to contain one letter and one digit or special character!")

            ###
            ### Here we actually change the password
            ###
            user = password_reset_request_obj.user
            user.password = regform.cleaned_data['password1']
            user.save()

            ###
            ### Here we update the password request
            ###
            password_reset_request_obj.already_used = True
            password_reset_request_obj.save()

            messages.add_message(request, messages.INFO, "Password reset for user: " + regform.cleaned_data['email'] + " was successful.")
            context = {
                'reset_passed': "TRUE"
            }
            template = loader.get_template(self.template_name)
            return HttpResponse(template.render(context, request))

        else:
            messages.add_message(request, messages.ERROR, "POST request without payload!")
            context = {}
            template = loader.get_template(self.template_name)
            return HttpResponse(template.render(context, request))


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField()

class PasswordResetRequestView(BaseView):
    template_name = "boilerplate/base_extensions/password_reset_request.html"

    '''
    Small function to put error message back to the user
    '''
    def return_error_and_prefill_form(self, request, regform, error_text):
        messages.add_message(request, messages.ERROR, error_text)
        context = {
            'email': regform.data['email']
        }
        template = loader.get_template(self.template_name)
        return HttpResponse(template.render(context, request))

    '''
    validate post entry, create user that is disabled and send email with activation
    '''
    def post(self, request, *args, **kwargs):
        if request.POST:
            regform = PasswordResetRequestForm(request.POST)
            if regform.is_valid():
                Logger.debug("PasswordResetRequestView - VALID input: " + regform.cleaned_data['email'])

            ##
            ## VALIDATE INPUT AND ANY ENFORCMENT IF YOU WANT
            ##
            if not regform.is_valid():
                # ERRORS IN FIELDS
                for field in regform.errors:
                    for error_text in regform.errors[field]:
                        messages.add_message(request, messages.ERROR, str(field) + ": " + str(error_text))
                        Logger.debug("PasswordResetRequestView -" + str(field) + ": " + str(error_text))

                # PREFILL FORM TO FIX
                context = {
                    'email': regform.data['email']
                }
                template = loader.get_template(self.template_name)
                return HttpResponse(template.render(context, request))

        ##
        ## Check if this user by chance already exists
        ##
        if not User.objects.filter(username=regform.cleaned_data['email']).first() and not User.objects.filter(email=regform.cleaned_data['email']).first():
            return self.return_error_and_prefill_form(request, regform, "User doesn't exist")
        ##
        ## Get the user
        ##
        user = User.objects.filter(username=regform.cleaned_data['email']).first()

        ##
        ## Everything passed, lets create user and send email to the user with activation link
        ##
        Logger.info("User " + regform.cleaned_data['email'] + " wants password reset.")

        ##
        ## Check if existing password reset already exists for this user and if it is still valid
        ## THIS IS A DOS PREVENTION WE DO NOT ALLOW PASSWORD RESET REQUEST UNTIL THE PREVIOUS ON EXPIRES
        ##
        previous_password_reset_object = PasswordResetRequest.objects.filter(user = user).last()
        if previous_password_reset_object is not None and previous_password_reset_object.is_not_old():
            Logger.info("PasswordResetRequestView: previous_password_reset_object " + str(previous_password_reset_object.id))
            return self.return_error_and_prefill_form(request, regform,
                                                      "DOS protection: Active password reset for this user exists")

        ## Create user password reset request object
        hash_object = hashlib.sha512((str(datetime.date.today().strftime("%B %d, %Y")) + regform.cleaned_data['email']).encode())
        hex_dig = hash_object.hexdigest()
        passwordresetrequest = PasswordResetRequest(activation_string=hex_dig, user=user, activation_requested_at=timezone.now())
        passwordresetrequest.save()

        ##
        ## Try to send password reset email, only if this works we actually write to database
        ##

        Logger.info("password reset for new user : " + regform.cleaned_data['email'] + " is " + hex_dig)
        try:
            sent_correctly_int_bool = send_mail(
                'password reset email',
                DOMAIN + 'accounts/password_reset/?key=' + hex_dig,
                EMAIL_SOURCE,
                [regform.cleaned_data['email']],
                fail_silently=False,
            )
            if sent_correctly_int_bool == 0:
                raise ValueError(
                    'send_mail function returned 0, but we needed 1 to know that the email went out.')
            else:
                passwordresetrequest.email_sent = True;
                passwordresetrequest.save()

        except Exception as error:
            Logger.error("Unable to send email to " + regform.cleaned_data['email'] + " and got exception: " + repr(error))
            return self.return_error_and_prefill_form(request, regform,
                                                      "We were unable to send out an activation email for this user, as such this user creation was deleted")

        ##
        ## Return back to password reset request view, but with "registration_passed" context
        ##
        messages.add_message(request, messages.INFO, "Password reset for user: " + regform.cleaned_data['email'] + " was created.")
        context = {
            'reset_email_sent': "TRUE"
        }
        template = loader.get_template(self.template_name)
        return HttpResponse(template.render(context, request))

class RegistrationForm(forms.Form):
    email = forms.EmailField()
    password1 = forms.CharField(max_length=64)
    password2 = forms.CharField(max_length=64)
    notes = forms.CharField(required=False)

class RegistrationView(BaseView):
    template_name = "boilerplate/base_extensions/registration.html"
    MIN_LENGTH = 8
    
    '''
    Small function to put error message back to the user
    '''
    def return_error_and_prefill_form(self, request, regform, error_text):
        messages.add_message(request, messages.ERROR, error_text )
        context = {
            'email' :regform.data['email']
            }                
        template = loader.get_template(self.template_name)
        return HttpResponse(template.render(context, request))        
    
    '''
    validate post entry, create user that is disabled and send email with activation
    '''
    def post(self, request, *args, **kwargs):
        if request.POST:
            regform = RegistrationForm(request.POST)
            if regform.is_valid():           
                Logger.debug("RegistrationView - VALID input: " +  regform.cleaned_data['email'] + " / " + regform.cleaned_data['password1'] + " / " + regform.cleaned_data['password2'])
            
            ##
            ## VALIDATE INPUT AND ANY ENFORCMENT IF YOU WANT
            ##
            if not regform.is_valid():
                # ERRORS IN FIELDS
                for field in regform.errors:
                    for error_text in regform.errors[field]:
                        messages.add_message(request, messages.ERROR, str(field) + ": " + str(error_text) )
                        Logger.debug("RegistrationView -" + str(field) + ": " + str(error_text))    
                
                # PREFILL FORM TO FIX
                context = {
                    'email' : regform.data['email']
                    }                
                template = loader.get_template(self.template_name)
                return HttpResponse(template.render(context, request)) 
            
            ##
            ## Check for password policies
            ##
            if regform.cleaned_data['password1'] != regform.cleaned_data['password2']:
                return self.return_error_and_prefill_form(request, regform, "Passwords do not match!")
            
            if len(regform.cleaned_data['password1']) < self.MIN_LENGTH:
                return self.return_error_and_prefill_form(request, regform, "Passwords is shorter than " + str(self.MIN_LENGTH) + "!" )
            
            first_isalpha = regform.cleaned_data['password1'].isalpha()
            if all(c.isalpha() == first_isalpha for c in regform.cleaned_data['password1']):
                return self.return_error_and_prefill_form(request, regform, "Password has to contain one letter and one digit or special character!")                                
                
         
        ## 
        ## Check if this user by chance already exists
        ##
        if User.objects.filter(username=regform.cleaned_data['email']).first() or User.objects.filter(email=regform.cleaned_data['email']).first():
            return self.return_error_and_prefill_form(request, regform, "This email is already registered")
         
        ##
        ## Everything passed, lets create user and send email to the user with activation link
        ##   
        Logger.info("New user wants registration, with " + regform.cleaned_data['email'] + " and email:" + regform.cleaned_data['email'])       
         
        ##
        ## Create user and activation associated entry
        ##
        hash_object = hashlib.sha512((str(datetime.date.today().strftime("%B %d, %Y")) + regform.cleaned_data['email']).encode())
        hex_dig = hash_object.hexdigest()          
        user=User.objects.create_user(regform.cleaned_data['email'], email=regform.cleaned_data['email'], password=regform.cleaned_data['password1'], is_superuser=False, is_staff=False, is_active = False)
        activation = Activation(activation_string=hex_dig,user=user,activation_requested_at=timezone.now())
        activation.save()          
         
        ##
        ## Try to send activation email, only if this works we actually write to database
        ##

        Logger.info("activation key for new user : " + regform.cleaned_data['email'] + " is " + hex_dig)           
        try:          
            sent_correctly_int_bool = send_mail(
                'activation email',
                DOMAIN + 'accounts/'+ str(user.id) +'/activation/?key='+hex_dig,
                EMAIL_SOURCE,
                [regform.cleaned_data['email']],
                fail_silently=False,
            )
            if sent_correctly_int_bool == 0:
                raise ValueError('send_mail function returned 0, but we needed 1 to know that the activation email went out.')
            else:
                activation.email_sent = True;
                activation.save()
            
        except Exception as error:
            Logger.error("Unable to send activation email to " + regform.cleaned_data['email'] + " and got exception: " + repr(error)) 
            return self.return_error_and_prefill_form(request, regform, "We were unable to send out an activation email for this user, as such this user creation was deleted")

        
        ##
        ## Return back to registration view, but with "registration_passed" context
        ##
        messages.add_message(request, messages.INFO, "New user: " + regform.cleaned_data['email'] + " was created." )
        context = {
            'registration_passed' : "TRUE"
            }                
        template = loader.get_template(self.template_name)
        return HttpResponse(template.render(context, request))         

            
class ActivationView(TemplateView):
    template_name = "boilerplate/base_extensions/activation.html"
    model = User
    context_object_name = 'user'
    extra_context = {}
    
    '''
    Small function to put error message back to the user
    '''
    def return_error(self, request, error_text):
        messages.add_message(request, messages.ERROR, error_text )
        context = {
            }                
        template = loader.get_template(self.template_name)
        return HttpResponse(template.render(context, request))     
    
    # 
    def get(self, request, *args, **kwargs): 
        
        if 'pk' not in kwargs:
            return self.return_error(request, "Invalid data in activation[01]")
            
        
        if kwargs.get('pk') == None:
            return self.return_error(request, "Invalid data in activation[01b]")
            
        
        user_obj = User.objects.get(pk=kwargs.get('pk'))     
        if user_obj is None:
            return self.return_error(request, "Invalid data in activation[02]")     
        
        if 'key' not in request.GET or not re.match(r"\b[a-f0-9]{128}\b", request.GET.get('key')):
            return self.return_error(request, "Invalid data in activation[03]")            
             
        key = request.GET.get('key')
        activation_obj = Activation.objects.get(user=user_obj.id)
            
        if activation_obj.activation_string != key:
            return self.return_error(request, "Invalid data in activation[04]")
        
        #
        # If you are down here, all passed and you can activate the user and give him a success message
        #            
        
        #activation 
        user_obj.is_active = True;
        user_obj.save()
        
        # reply to user
        context = {
            'result': 'success',
        }         
        context.update(self.extra_context)                
       
        template = loader.get_template(self.template_name)
        return HttpResponse(template.render(context, request))            
                          
