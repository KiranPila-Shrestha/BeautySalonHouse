from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.forms import User
from django import forms
from django.urls import reverse_lazy
from .models import UserProfile
from django.contrib.auth.views import PasswordChangeView

class CreateUserForm(UserCreationForm):
    profile_picture = forms.ImageField(required=False)
    class Meta:
        model= User
        fields = ['first_name', 'last_name','username', 'email', 'password1', 'password2',]
        
class UserUpdateForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False)
    class Meta:
        model= User
        fields = ['first_name', 'last_name','username', 'email']
    
class ProfileUpadateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']
        
        
class PasswordChangeView(PasswordChangeView):
    from_class = PasswordChangeForm
    success_url = reverse_lazy('/')   