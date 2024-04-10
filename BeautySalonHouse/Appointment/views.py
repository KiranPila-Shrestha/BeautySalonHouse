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
import sweetify
from django.db.models import Count

# Create your views here.

# booking by customer views.
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
                sweetify.error(request, 'Please fill out all required fields.')
                print("Missing required fields")
                return render(request, 'landing_page/Booking.html')
                # Combine the selected date and time
            selected_datetime = timezone.make_aware(timezone.datetime.strptime(booked_date + ' ' + booked_time, '%Y-%m-%d %H:%M'))

            if selected_datetime < timezone.now():
                sweetify.error(request, 'Please select a time in the future.')
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
                sweetify.success(request, 'Appointment has been sent for approval. You will be notified about confirmation.', extra_tags='success')
            
                return render(request, 'landing_page/Booking.html')
            except:
                #  error message if appointment fails to book
                sweetify.error(request, 'Failed to book appointment. Please try again later.')
         
                return render(request, 'landing_page/Booking.html')
         
    booking_requests = BookAppointment.objects.all()
    userAndUserType = User.objects.all()
    context = {
        "userAndUserType" : userAndUserType,

        # 'form':form
    }
    
    return render(request, 'landing_page/Booking.html', context)

#appointment cancel and approve handling vies by stafff.

def Appointments(request):
 
    booking_requests = BookAppointment.objects.filter(staff=request.user, confirmed=False, status="Pending")
    
    if request.method == 'POST':
        bookingId = request.POST.get("bookingId")
        booking = BookAppointment.objects.get(id=bookingId, confirmed=False, status="Pending")
        print(booking)
        
        if "cancel" in request.POST:
            # Mark the appointment as canceled
            booking.status = 'Canceled'
            booking.Canceled = True
            booking.save()
            
            # Save the details in the canceled appointments model
            canceled_booking = CanceledAppointment.objects.create(
                user=booking.user,
                appointment=booking,
                canceledDate=timezone.now()
            )
            canceled_booking.save()
            
            send_mail(
                'Appointment is Rejected',
                'Your appointment has been rejected by the staff member',
                settings.EMAIL_HOST_USER,
                [booking.user.email],
                fail_silently=False,
            )
            
        if "approve" in request.POST:
            booking.confirmed = True
            booking.status = 'confirm'
            booking.save()
            send_mail(
                'Appointment has been Approved',
                'Your appointment has been approved by the staff member on the date and time you have chosen',
                settings.EMAIL_HOST_USER,
                [booking.user.email],
                fail_silently=False,
                
            )
            print('done')
            return redirect("appointments")
          
    
    context = {
        "booking_requests": booking_requests,

    }
    return render(request, 'Staff/Technican_Dashboard.html', context)


#display all the cancel appointment

def CancelAppointments(request):
    # Retrieve all canceled appointments
    canceled_appointments = BookAppointment.objects.filter(staff=request.user, status='Canceled')
    
    context = {
        'canceled_appointments': canceled_appointments
    }
    
    return render(request, 'Staff/cancel_appointment.html', context)

# Complete Appointments view
def CompleteAppointments(request):
    currentUser = str(request.user)

    completed_appointments = BookAppointment.objects.filter(staff=currentUser, status="completed")
    print("abcdddddddddddeeeeeeeeeee: ", completed_appointments)
    context = {
        "completed_appointments": completed_appointments,
    }
    return render(request, 'Staff/completedappointment.html', context)


# See all the confirm appointment dashboard logic for staff and admin and customer.

@login_required
def bookedAppointment(request, user_id=None):
    currentUser = str(request.user)
    print(currentUser)
    #add status complete one after approve
    if request.method == "POST" and "complete" in request.POST:
        appID = request.POST.get("appointmentID")
        print("appID", appID)
        booking_requests = BookAppointment.objects.get(pk=appID)
        booking_requests.status = "completed"
        booking_requests.save()
        print("booking_requests", booking_requests)
    #views after showing the appointment cancels after approve
    if request.method == "POST" and "cancel" in request.POST:
        book_id = request.POST.get("appointmentID")
        print("datttt", book_id)
        booking_requests = BookAppointment.objects.get(pk=book_id)
        booking_requests.status = "cancel Booking"
        booking_requests.save()
        print("canelkooooo",booking_requests)
        
    
    
    if request.user.is_superuser:
        # For admin
        booking_requests = BookAppointment.objects.filter(confirmed=True)
        distinct_statuses = booking_requests.values('status').annotate(count=Count('status'))
        distinct_services = booking_requests.values('service').annotate(count=Count('service'))

        template_name = 'Admin_Page/adminAppointment.html'
        
    elif request.user.groups.filter(name__in=["Hair Technician", "Laser Skin", "Nail Technician", "Makeup Artist"]).exists():
        # For staff members
        booking_requests = BookAppointment.objects.filter(staff=currentUser, status="confirm")
        distinct_statuses = []  # Initialize distinct_statuses
        distinct_services = []  # Initialize distinct_services
        print("booking_requestsbooking_requestsbooking_requests:", booking_requests)
        template_name = 'Staff/technicianAppointmentHistory.html'
    else:
        # For regular customers
        if user_id is not None:
            booking_requests = BookAppointment.objects.filter(user_id=user_id, confirmed=True)
        else:
            booking_requests = BookAppointment.objects.filter(user=request.user, confirmed=True)
            print(booking_requests)
        template_name = 'User_Profile_Management/appointmenthistory.html'
    current_date = datetime.now().date()  # Get current date
    context = {
        "booking_requests": booking_requests,
        "user_id": user_id,
        "current_date": current_date, 
        'distinct_statuses': distinct_statuses,
        'distinct_services': distinct_services# Pass current date to template
    }
    return render(request, template_name, context)

# views after showing the appointment cancels after approve data showing
def CancelbookedAppointement(request):
    # Retrieve all canceled appointments
    canceled_booked_appointment = BookAppointment.objects.filter(staff=request.user, status='cancel Booking')
    print("aoooooooooo",canceled_booked_appointment)
    
    context = {
        'canceled_booked_appointment': canceled_booked_appointment
    }
    
    return render(request, 'Staff/cancel_bookedAppointment.html', context)


def userCancelbookedAppointement(request):
    # Retrieve all canceled appointments
    user_canceled_booked_appointment = BookAppointment.objects.filter(user=request.user, status='cancel Booking')
    print("aoooooooooo",user_canceled_booked_appointment)
    
    context = {
        'user_canceled_booked_appointment': user_canceled_booked_appointment
    }
    
    return render(request, 'User_Profile_Management/Rejectedappointment.html', context)

# views for appointment information for user only.

def appointmentHistory(request):
    #filter appoint of current user
    booking_requests = BookAppointment.objects.filter(user= request.user)

    context = {

        'booking_requests' : booking_requests,

        }


    return render(request, 'User_Profile_Management/appointmenthistory.html', context)

    

#user history of complete appointment.


def UserCompleteAppointments(request):
    userFeedBack = None
    feedback = None
    
    if request.method == 'POST' and 'submitFeedback' in request.POST:
        bookingID = request.POST.get('bookingId')
        feedback_text = request.POST.get('feedback')
        
        booking = get_object_or_404(BookAppointment, id=bookingID)
        
        # Check if user has already given feedback for this booking
        AppointmentFeedback.objects.create(user=request.user, appointment=booking, feedback=feedback_text)
        sweetify.success(request, 'Feedback has been submitted successfully.')
        return redirect('Usercompleteappointments') 
        # if existing_feedback.exists():
        #     print("ghs bdc")
        #     # Update existing feedback
        #     existing_feedback.update(feedback=feedback_text)
        #     messages.success(request, 'Feedback has been added successfully to our service page.')
        # else:
        #     # Add new feedback
        #     feedback = AppointmentFeedback(appointment=booking, user=request.user, feedback=feedback_text)
        #     feedback.save()
        #     messages.success(request, 'Feedback has been submitted successfully.')
        # return redirect('Usercompleteappointments') 
    
    booking_complete = BookAppointment.objects.filter(user=request.user)
    
    for booking_request in booking_complete:
        userFeedBack = AppointmentFeedback.objects.filter(user=request.user, appointment=booking_request)
        feedback = AppointmentFeedback.objects.filter(user=request.user)
        
    if userFeedBack:
        print("Existing feedback:", userFeedBack)
   
    completed_appointment_user = BookAppointment.objects.filter(user=request.user, status= 'completed')
    print("Completed appointments:", completed_appointment_user)
    
    context = {
        "completed_appointment_user": completed_appointment_user,
        'userFeedBack': userFeedBack,
        'feedback': feedback,
    }
    return render(request, 'User_Profile_Management/Usercompletedappointment.html', context)
