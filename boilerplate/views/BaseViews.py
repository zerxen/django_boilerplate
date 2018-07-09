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


class BaseView(TemplateView):
    template_name = "boilerplate/base_template.html"
    model = User
    context_object_name = 'user'
    extra_context = {}
    
    # 
    def get(self, request, *args, **kwargs): 
        
        # JSUT IN CASE
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
                state = "Inactive account"            
                HttpResponseForbidden("Invalid account")
        
        # GENERIC RETURN           
        return redirect(request.path)    
    
class LogoutView(BaseView):
    def get(self, request, *args, **kwargs): 
        logout(request)
        # Redirect to a success page.
        return redirect('index') 

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
        ## Everything passed, lets create user and send email to the user with activation link
        ##   
        Logger.info("New user wants registration, with " + regform.cleaned_data['email'] + " and email:" + regform.cleaned_data['email'])       
        
        # local admin creation
        if User.objects.filter(username=regform.cleaned_data['email']).first() or User.objects.filter(email=regform.cleaned_data['email']).first():
            return self.return_error_and_prefill_form(request, regform, "This email is already registered")
        
        user=User.objects.create_user(regform.cleaned_data['email'], email=regform.cleaned_data['email'], password=regform.cleaned_data['password1'], is_superuser=False, is_staff=False, is_active = False)
        hash_object = hashlib.sha512((str(user.date_joined) + user.email).encode())
        hex_dig = hash_object.hexdigest()
        Logger.info("activation key: " + hex_dig)
        user.last_name = hex_dig
        user.save() 
        
        ##
        ## Send activation email
        ##       
        import code
        code.interact(local=locals())        
        send_mail(
            'activation email',
            'https://networkgeekstuff.com/?activate='+user.last_name,
            'activation@networkgeekstuff.com',
            [user.email],
            fail_silently=False,
        )
        
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
    template_name = "boilerplate/base_template.html"
    model = User
    context_object_name = 'user'
    extra_context = {}
    
    # 
    def get(self, request, *args, **kwargs): 
        
        # JSUT IN CASE
        initialization.initialization()
        
        context = {
            self.context_object_name: request.user,
        }         
        context.update(self.extra_context)                
       
        template = loader.get_template(self.template_name)
        return HttpResponse(template.render(context, request))            
                          
