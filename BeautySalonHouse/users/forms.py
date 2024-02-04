from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import User
from django import forms
from .models import UserProfile

class CreateUserForm(UserCreationForm):
    profile_picture = forms.ImageField(required=False)
    class Meta:
        model= User
        fields = ['first_name', 'last_name','username', 'email', 'password1', 'password2',]
        
# class UserUpdateForm(forms.ModelForm):
#     profile_picture = forms.ImageField(required=False)
#     class Meta:
#         model= User
#         fields = ['first_name', 'last_name','username', 'email']
    
# class ProfileUpadateForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = ['image']