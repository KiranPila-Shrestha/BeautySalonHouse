from django.db import models
from django.contrib.auth.models import AbstractUser, User, Group
from django.utils import timezone



    


class UserDetail(models.Model):
   """
   In Django, when you define a ForeignKey or OneToOneField in a model, the related 
   objects are accessible using a lowercased version of the target model's name. 
   This is part of Django's default naming conventions.
   """
   
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   address = models.CharField(max_length=255,blank=False)
   contact_number = models.CharField(max_length=15,blank=False)
   user_type = models.CharField(max_length=15,blank=False, default="customer")
   reward_points = models.IntegerField(default=0)
   hasUserBlocked = models.BooleanField(default=False)
   
   def __str__(self):
        return f"{self.user.username}'s Details"
     
class UserProfile(models.Model):
   
   """there is one to one relation between user and profile"""
   user = models.OneToOneField(User, on_delete = models.CASCADE)
   image = models.ImageField(default='default_image/profiledefault.jpg', blank=False, upload_to='profile_pics')
   
   def __str__(self):
      return f'{self.user.username} UsersProfile'


   