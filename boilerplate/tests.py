from django.test import TestCase
from django.core.mail import send_mail
from boilerplate.settings import *
from django.test import Client
from boilerplate.models import *

# Create your tests here.


class EmailTests(TestCase):

    def test_email_backend_working(self):
        """
        Try sending a small email to me on zerxen@networkgeekstuff.com
        """
        sent_correctly_int_bool = send_mail(
            'test email subject',
            'test content',
            EMAIL_SOURCE,
            ['zerxen@networkgeekstuff.com'],
            fail_silently=False,
        )

        self.assertIs(sent_correctly_int_bool, 1)
        
        
    
class RegistrationTests(TestCase):

    def test_registration_correct(self): 
        client = Client()
        
        '''
        Going for registration to get redirect to login
        '''        
        response = client.get('/accounts/registration/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form action="/accounts/registration/" method="post">', 1)
        
        
        ''' 
        Lets try registering someone and check if he gets good response
        '''
        response = client.post("/accounts/registration/", {'email':'zerxen@pingonyou.com', 'password1':'blbost123', 'password2':'blbost123' })         
        self.assertContains(response, 'You have submitted you regstration, to activate you account follow a link that we sent to your email account.', 1)
        
        '''
        Getting activation key via logs
        '''
        
        user_obj = User.objects.filter(username='zerxen@pingonyou.com')[0]
        activation_obj = Activation.objects.get(user=user_obj.id)
       

        ''' 
        activate user
        '''
        url = '/accounts/'+ str(user_obj.id) +'/activation/?key=' + str(activation_obj.activation_string) 
        response = client.get(url)
        self.assertContains(response, 'You account was activated')
        

    def test_login_correct(self): 
        client = Client()
        
        '''
        Going for index to get redirect to login
        '''
        response = client.get('/')
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/accounts/login/?next=/') 
        
        
        response = client.get('/accounts/login/?next=/')
        self.assertContains(response, '<form action="/accounts/login/" method="post">')
        
        
        response = client.post("/accounts/login/", {'username':'zerxen@pingonyou.com', 'password':'blbost123', 'next':'/' }) 
        
        '''
        successfull login gives us redirect to the /
        '''
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')        
        
        
              
