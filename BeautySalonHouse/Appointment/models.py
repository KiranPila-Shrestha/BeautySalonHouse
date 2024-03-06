from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone



class BookAppointment(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    service = models.CharField(max_length=255, blank=False)
    staff = models.CharField(max_length=255, blank=False)
    bookDate = models.DateField(default=timezone.now)
    bookTime = models.TimeField(default=timezone.now)
    description = models.TextField(blank= True, null=True)
    confirmed = models.BooleanField(default=False)
   
    def __str__(self) -> str:
      return f"{self.user}'s Pending"
   

# Create your models here.
