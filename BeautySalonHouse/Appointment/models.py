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
    status = models.CharField(max_length=255,default='Pending')
   
    def __str__(self) -> str:
      return f"{self.service} by {self.user.username}"
    
    
class AppointmentFeedback(models.Model):
    appointment = models.ForeignKey(BookAppointment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback = models.TextField(blank=True)
    
    def __str__(self):
      return f"Feedback for {self.appointment} by {self.user.username}"
   

# Create your models here.
