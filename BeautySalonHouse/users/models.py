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
   
   def __str__(self):
        return f"{self.user.username}'s Details"
     
class UserProfile(models.Model):
   
   """there is one to one relation between user and profile"""
   user = models.OneToOneField(User, on_delete = models.CASCADE)
   image = models.ImageField(default='default_image/profiledefault.jpg', blank=False, upload_to='profile_pics')
   
   def __str__(self):
      return f'{self.user.username} UsersProfile'

# class ServiceDetail(models.Model):
#    name = models.CharField(max_length=100)
#    description = models.TextField()
#    price = models.DecimalField(max_digits=8, decimal_places= 2)
   
#    def __str__(self) -> str:
#       return f'{self.service.name}'

# class Staff(models.Model):
#    user = models.OneToOneField(User, on_delete = models.CASCADE)
#    role = models.CharField(max_length = 100)
   
#    def __str__(self):
#       return f'{self.user.username}' - '{self.role}'


# class BookAppointment(models.Model):
#    user = models.ForeignKey(User, on_delete = models.CASCADE ,related_name='booked_appointments')
#    service = models.ForeignKey(ServiceDetail, related_name='service_appointment', on_delete=models.CASCADE)
#    staff = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_appointment')
#    hair_type = models.CharField(max_length=100, default = 'Straight')
#    skin_type = models.CharField(max_length = 100, default = 'normal')
#    skin_problem = models.TextField(max_length=100, default = 'None')
#    BookDate = models.DateField(default=timezone.now)
#    confirmed = models.BooleanField(default=False)
   
#    def __str__(self) -> str:
#       return f"{self.user}'s Pending"
   
   
