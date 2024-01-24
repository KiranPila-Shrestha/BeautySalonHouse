from django.db import models
from django.contrib.auth.models import User



    


class UserDetail(models.Model):
   """
   In Django, when you define a ForeignKey or OneToOneField in a model, the related 
   objects are accessible using a lowercased version of the target model's name. 
   This is part of Django's default naming conventions.
   """
   
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   address = models.CharField(max_length=255,blank=False)
   contact_number = models.CharField(max_length=15,blank=False)
   
   def __str__(self):
        return f"{self.user.username}'s Details"