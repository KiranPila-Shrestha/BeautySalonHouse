from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.models import Group


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
            description = request.POST.get('description')
            print("Service:", service)
            print("Staff:", staff)
            print("Booked Date:", booked_date)
            print("Booked Time:", booked_time)
            print("Description:", description)
        
            
            if not service or not staff or not booked_date or not booked_time:
                messages.error(request, 'Please fill out all required fields.')
                print("Missing required fields")
                return render(request, 'landing_page/Booking.html')
                # Combine the selected date and time
            selected_datetime = timezone.make_aware(timezone.datetime.strptime(booked_date + ' ' + booked_time, '%Y-%m-%d %H:%M'))

            if selected_datetime < timezone.now():
                messages.error(request, 'Please select a time in the future.')
                print("Selected time is in the past")
                return render(request, 'landing_page/Booking.html')
            # Show error message if selected datetime is in the past
            
            
            appointment_book = BookAppointment(
                user=user,
                service=service,
                staff=staff,
                bookDate=booked_date, 
                bookTime=booked_time,
                description =description 
            )
           
            try:
                appointment_book.save()
                #  success message
                messages.success(request, 'Appointment has been sent for approval. You will be notified about confirmation.', extra_tags='success')
            
                return render(request, 'landing_page/Booking.html')
            except:
                #  error message if appointment fails to book
                messages.error(request, 'Failed to book appointment. Please try again later.')
         
                return render(request, 'landing_page/Booking.html')
         
    booking_requests = BookAppointment.objects.all()
    userAndUserType = User.objects.all()
    context = {
        "userAndUserType" : userAndUserType,

        # 'form':form
    }
    
    return render(request, 'landing_page/Booking.html', context)



def Appointments(request):
    booking_requests = BookAppointment.objects.filter(staff=request.user, confirmed=False)

    
    if request.method == 'POST':
        bookingId = request.POST.get("bookingId")
        booking = BookAppointment.objects.get(id=bookingId)
        print(booking)
        
        if "delete" in request.POST:
            booking.delete()
            send_mail(
                'Appointment is Rejected',
                'Your appointment has been rejected by the staff member',
                settings.EMAIL_HOST_USER,
                [booking.user.email],
                fail_silently=False,
            )
            
        if "approve" in request.POST:
            booking.confirmed = True
            booking.save()
            send_mail(
                'Appointment has been Approved',
                'Your appointment has been approved by the staff member on the date and time you have chosen',
                settings.EMAIL_HOST_USER,
                [booking.user.email],
                fail_silently=False,
                
            )
            print('done')
            booking_requests = BookAppointment.objects.filter(staff=request.user, confirmed=True)   
            return redirect("appointments")
          
    
    context = {
        "booking_requests": booking_requests,

    }
    return render(request, 'Staff/Technican_Dashboard.html', context)


# def feedback(request):
#     if request.method == "POST":
#         bookingId = request.POST.get("bookingId")
#         feedbackText = request.POST.get("feedback")
#         booking = BookAppointment.objects.get(id=bookingId)
        
#         #save feedback
#         if feedbackText:
#             AppointmentFeedback.objects.create(appointment=booking, user=request.user, feedback=feedbackText)
#             messages.success(request, 'Feedback has been submitted successfully.')
#         else:
#             messages.error(request, 'Feedback cannot be empty')
        
#         return redirect('appointmenthistory')
#     return render(request, 'appointmenthistory')


@login_required
def bookedAppointment(request, user_id=None):
    if request.user.is_superuser:
        # For admin
        booking_requests = BookAppointment.objects.filter(confirmed=True)
        template_name = 'Admin_Page/adminAppointment.html'
    elif request.user.groups.filter(name__in=["Hair Technician", "Laser Skin", "Nail Technician", "Makeup Artist"]).exists():
        # For staff members
        booking_requests = BookAppointment.objects.filter(staff=request.user, confirmed=True)
        template_name = 'Staff/technicianAppointmentHistory.html'
    else:
        # For regular customers
        if user_id is not None:
            booking_requests = BookAppointment.objects.filter(user_id=user_id, confirmed=True)
        else:
            booking_requests = BookAppointment.objects.filter(user=request.user, confirmed=True)
        template_name = 'User_Profile_Management/appointmenthistory.html'
    current_date = datetime.now().date()  # Get current date
    context = {
        "booking_requests": booking_requests,
        "user_id": user_id,
        "current_date": current_date,  # Pass current date to template
    }
    return render(request, template_name, context)


   

#User Appointment History    
def appointmentHistory(request):
    if request.method == 'POST' and 'submitFeedback' in request.POST:
        bookingID = request.POST.get('bookingId')
        feedback = request.POST.get('feedback')
        
        booking = get_object_or_404(BookAppointment, id=bookingID)
        feedback = AppointmentFeedback(appointment=booking, user=request.user, feedback=feedback)
        feedback.save()
        messages.success(request, 'Feedback has been submitted successfully.')
        
    
        print("POST VAKO XA",bookingID, feedback)
    
    
    
    booking_requests = BookAppointment.objects.filter(user= request.user)
    
    hasCompletedAppointments = BookAppointment.objects.filter(user= request.user, status= 'Confirmed').exists()
    
    currentDate = datetime.now().date()
    
    for booking_request in booking_requests:
        if booking_request.bookDate < currentDate:
            bookings = BookAppointment.objects.filter(user= request.user, bookDate= booking_request.bookDate)
            for booking in bookings:
                booking.status = 'Confirm'
                booking.save()
            
        else:
            bookings = BookAppointment.objects.filter(user= request.user, bookDate= booking_request.bookDate)
            for booking in bookings:
                booking.status = 'Pending'
                booking.save()
         
    for booking_request in booking_requests:

        userFeedBack = AppointmentFeedback.objects.filter(user= request.user, appointment = booking_request)
        feedback = AppointmentFeedback.objects.filter(user= request.user)
        if(userFeedBack):
            print("aaaaaaaaaaaaaaaaaaa", userFeedBack )


        
    context = {
        'hasCompletedAppointments' : hasCompletedAppointments,
        'booking_requests' : booking_requests,
        'userFeedBack' : userFeedBack,
        'feedback' : feedback,
        }

    
    return render(request, 'User_Profile_Management/appointmenthistory.html', context)   
 

 

    
#staff appointment History
def staffappointmentHistory(request, user_id):
    
    return render(request, 'Staff/technicianAppointmentHistory.html')



# hair-technician dashboard started
def HairStaffDashboard(request):
    return render(request, 'Staff/Technican_Dashboard.html')
