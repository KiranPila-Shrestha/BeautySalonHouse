from django.urls import path
from . import views
# PASSWORD RESET
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login', views.loginUser, name='login'),
    path('logout', views.logoutUser, name='logout'),
    # path('logout', views.logoutUser, name='logout'),
    path('register', views.registerUser, name='register'),
    
     path('AdminDashBoard/', views.AdminDashBoard, name='AdminDashBoard'),
    
   
   path('EditProfile/', views.EditProfile, name='EditProfile'),
 
    # FOR Admin
    # path('adminHome', views.adminHome, name='adminHome'),   
     
       
    
    
]