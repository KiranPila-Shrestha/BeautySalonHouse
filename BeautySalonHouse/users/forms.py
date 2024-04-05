from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.forms import User
from django import forms
from django.urls import reverse_lazy
from .models import *
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


    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user