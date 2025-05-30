from django.urls import path
from . import views

# PASSWORD RESET
from django.contrib.auth import views as auth_views
urlpatterns = [ 
               path('Bookingappointment', views.booking, name='booking'),
               path('appointmenthistory/', views.appointmentHistory, name='appointmenthistory'),
               path('staffappointmenthistory/', views.bookedAppointment, name='staffappointmenthistory'),
               path('adminappointmenthistory/', views.bookedAppointment, name='adminAppointmenthistory'),
               path('appointments', views.Appointments, name='appointments'),
               path('completeappointments', views.CompleteAppointments, name='completeappointments'),
               path('Cancelappointments', views.CancelAppointments, name='Cancelappointments'),
               path('CancelbookedAppointement', views.CancelbookedAppointement, name='CancelbookedAppointement'),
               #userr...
                path('Usercompleteappointments', views.UserCompleteAppointments, name='Usercompleteappointments'),
                path('userCancelbookedAppointement', views.userCancelbookedAppointement, name='userCancelbookedAppointement'),
                path('userRejectAppointement', views.RejectAppointment, name='userRejectAppointement'),
                
               
         
               
                ]

