"""boilerplate URL Configuration

The `urlpatterns` list routes URLs to views_classes. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views_classes
    1. Add an import:  from my_app import views_classes
    2. Add a URL to urlpatterns:  path('', views_classes.home, name='home')
Class-based views_classes
    1. Add an import:  from other_app.views_classes import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from boilerplate.views.BaseViews import BaseView,LoginView,LogoutView,RegistrationView,ActivationView


urlpatterns = [

    ## BASIC LOGIN/LOGOUT
    re_path(r'^accounts/login/$', LoginView.as_view(), name='login'),
    re_path(r'^$', login_required(BaseView.as_view()), name='index'),
    re_path(r'^accounts/logout/$', login_required(LogoutView.as_view()), name='logout'), 
    
    ## REGISTRATION
    re_path(r'^accounts/registration/$', RegistrationView.as_view(), name='registration'),
    re_path(r'^accounts/activation/$', ActivationView.as_view(), name='activation'),
    
    ## ADMIN AREA
    path('admin/', admin.site.urls),
    
]
