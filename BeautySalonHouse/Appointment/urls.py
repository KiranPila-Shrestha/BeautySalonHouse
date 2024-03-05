from django.urls import path
from . import views

# PASSWORD RESET
from django.contrib.auth import views as auth_views
urlpatterns = [ 
               path('booking', views.booking, name='booking'),]

