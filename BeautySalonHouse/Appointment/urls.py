from django.urls import path
from . import views

# PASSWORD RESET
from django.contrib.auth import views as auth_views
urlpatterns = [ 
               path('booking/', views.booking, name='booking'),
               path('StaffDashboard', views.HairStaffDashboard, name='HairStaffDashboard'),
               path('appointmenthistory/', views.appointmentHistory, name='appointmenthistory'),
               path('staffappointmenthistory/', views.bookedAppointment, name='staffappointmenthistory'),
               path('adminappointmenthistory/', views.bookedAppointment, name='adminAppointmenthistory'),
               path('appointments', views.Appointments, name='appointments'),
                 path('completeappointments', views.CompleteAppointments, name='completeappointments'),
                 path('Usercompleteappointments', views.UserCompleteAppointments, name='Usercompleteappointments'),
                  path('Cancelappointments', views.CancelAppointments, name='Cancelappointments'),
            #    path('feedback', views.feedback, name='feedback'),
               
                ]

