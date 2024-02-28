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
    

# class StaffCreationForm(forms.ModelForm):
#     first_name = forms.CharField(label='First Name', max_length=100)
#     last_name = forms.CharField(label='Last Name', max_length=100)
#     address = forms.CharField(label='Address', widget=forms.Textarea)
#     staff_role = forms.ChoiceField(label='Staff Role', choices=[
#         ('', 'Select staff role'),
#         ('Hair Technician', 'Hair Technician'),
#         ('Makeup Artist', 'Makeup Artist'),
#         ('Nail Technician', 'Nail Technician'),
#         ('Laser Skin', 'Laser Skin')
#     ])
#     password = forms.CharField(label='Password', widget=forms.PasswordInput)
#     confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

#     class Meta:
#         model = StaffDetails
#         fields = ['first_name', 'last_name', 'address', 'staff_role', 'password', 'confirm_password']


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