from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    
    path('contact', views.contact, name='contact'),
    path('service', views.service, name='service'),
    path('hairservice', views.hairservice, name='hairservice'),
    path('makeupservice', views.makeupservice, name='makeupservice'),
    path('nailservice', views.nailservice, name='nailservice'),
    path('skinservice', views.skinservice, name='skinservice'),
    
]
