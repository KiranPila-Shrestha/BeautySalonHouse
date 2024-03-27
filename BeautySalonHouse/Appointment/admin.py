from django.contrib import admin
from Appointment.models import *

# Register your models here.
admin.site.register(BookAppointment)
admin.site.register(AppointmentFeedback)
admin.site.register( CanceledAppointment)
