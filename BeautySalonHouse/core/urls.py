from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.index, name='home'),
     path('booking', views.booking, name='booking'),
     path('product', views.product, name='product'),
    path('contact', views.contact, name='contact'),
    
]
