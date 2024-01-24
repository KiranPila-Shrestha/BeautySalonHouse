from django.urls import path
from . import views
# PASSWORD RESET
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login', views.loginUser, name='login'),
    path('logout', views.logoutUser, name='logout'),
    # path('logout', views.logoutUser, name='logout'),
    path('register', views.registerUser, name='register'),
    # FOR Admin
    # path('adminHome', views.adminHome, name='adminHome'),   
     
       
    
    
]