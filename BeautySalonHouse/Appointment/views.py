from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render,redirect, get_object_or_404


from datetime import datetime
from django.utils import timezone
from django.contrib import messages
# IMPORTING "update_session_auth_hash" to Change PASSWORD
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from users.models import *
from Appointment.models import *

from django.db import transaction
from django.contrib.auth.models import User

# SEND MAIL
from django.core.mail import send_mail
from django.conf import settings


# Create your views here.


def booking(request): 
    username = request.POST.get('username')
    user = request.user 
    print(user)
    if request.method == "POST":
        
        if request.method == "POST":
            user = request.user
            service = request.POST.get('service')
            staff = request.POST.get('staff')
            booked_date = request.POST.get('BookDate')
            booked_time = request.POST.get('BookTime')
            
            appointment_book = BookAppointment(
                user=user,
                service=service,
                staff=staff,
                bookDate=booked_date,  # Correct field name
                bookTime=booked_time     # Correct field name
            )
            appointment_book.save()
            
            return render(request, 'landing_page/Booking.html')
         
    booking_requests = BookAppointment.objects.all()
    userAndUserType = User.objects.all()
    context = {
        "userAndUserType" : userAndUserType,

        # 'form':form
    }
    
    return render(request, 'landing_page/Booking.html', context)



def Appointments(request):
    booking_requests = BookAppointment.objects.filter(staff=request.user)
    
    if request.method == 'POST':
        bookingId = request.POST.get("bookingId")
        booking = BookAppointment.objects.get(id=bookingId)
        print(booking)
        
        if "delete" in request.POST:
            booking.delete()
            
        if "approve" in request.POST:
            booking.confirmed = True
            booking.save()
            print('done')
            
        booking_requests = BookAppointment.objects.filter(staff=request.user, confirmed=False)   
            
          
            
      
        
    
    
    context = {
        "booking_requests": booking_requests,

    }
    return render(request, 'Staff/Hair_Technican_Dashboard.html', context)



 # if request.method == 'POST':
    #     form = BookAppointmentForm(request.POST)
    #     if form.is_valid():
    #         service_id = form.cleaned_data['service']
    #         staff_id = form.cleaned_data['staff']
    #         BookDate = form.cleaned_data['BookDate']
    #         #BookDate = datetime.strptime(BookDate_str, '%m/%d/%Y').date()  # Convert string to datetime object
    #         BookTime = form.cleaned_data['BookTime']
            
    #         # retrives service and staff instance
            
    #         service = get_object_or_404(pk=service_id)
    #         staff = get_object_or_404(pk=staff_id)
            
    #         with transaction.atomic():
    #             appointment = BookAppointment.objects.create(
    #                 user = request.user,
    #                 service = service,
    #                 staff = staff,
    #                 BookDate = BookDate,
    #                 BookTime = BookTime,
    #                 hair_type=request.POST.get("hair_type"),
    #                 skin_type=request.POST.get("skin_type"),
    #                 skin_problem=request.POST.get("skin_problem"),
    #                 confirmed=False
    #             )
    #             print("1")
    #             appointment.save()
    #             print("2")
            
    #         messages.success(request, 'Appointment booked successfully!')
    #         return redirect('landing_page/booking.html')
    #     else:
    #         messages.error(request, 'Invalid form data. Please check the form and try again.')
    # else:
    #      form = BookAppointmentForm()  
    
#staff appointment History
def AppointmentHistory(request):
    
    return render(request, 'Staff/HairAppointmentHistory.html')
