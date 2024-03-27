from django.urls import path
from . import views
# PASSWORD RESET
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login', views.loginUser, name='login'),
    path('logout', views.logoutUser, name='logout'),
    # path('logout', views.logoutUser, name='logout'),
    path('register', views.registerUser, name='register'),
    path('EditProfile/<int:user_id>/', views.EditProfile, name='EditProfile'),
    path('StaffEditProfile/<int:user_id>/', views.EditProfile, name='StaffEditProfile'),

    path('ChangePassword/<int:user_id>/', views.ChangePassword, name= 'ChangePassword'),
    
    # PASSWORD RESET
    path('reset_password', auth_views.PasswordResetView.as_view(
    template_name="Login_Register/Reset_Password/ResetPassword.html"), 
    name="reset_password"),   
    
    path('reset_password_sent', auth_views.PasswordResetDoneView.as_view(
    template_name="Login_Register/Reset_Password/SentPasswordReset.html"), 
    name="password_reset_done"), 
      
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
    template_name="Login_Register/Reset_Password/ConfirmResetPassword.html"), 
    name="password_reset_confirm"), 
      
    path('reset_password_complete', auth_views.PasswordResetCompleteView.as_view(
    template_name="Login_Register/Reset_Password/ResetPasswordNext.html"), 
    name="password_reset_complete"),  
    
    # For admin pathhh..
    path('AdminDashBoard/', views.AdminDashBoard, name='AdminDashBoard'),
    
 

    
]