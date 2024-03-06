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
            
            if not service or not staff or not booked_date or not booked_time:
                messages.error(request, 'Please fill out all required fields.')
                return render(request, 'landing_page/Booking.html')
            
            appointment_book = BookAppointment(
                user=user,
                service=service,
                staff=staff,
                bookDate=booked_date,  # Correct field name
                bookTime=booked_time,
                description =description # Correct field name
            )
           
            try:
                appointment_book.save()
                # Add success message
                messages.success(request, 'Appointment has been sent for approval. You will be notified about confirmation.')
                # Redirect to a different URL after booking
                return render(request, 'landing_page/Booking.html')
            except:
                # Add error message if appointment fails to book
                messages.error(request, 'Failed to book appointment. Please try again later.')
                # Redirect or render booking page with error message
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
            
        if "approve" in request.POST:
            booking.confirmed = True
            booking.save()
            print('done')
            booking_requests = BookAppointment.objects.filter(staff=request.user, confirmed=True)   
            return redirect("appointments")
          
    
    context = {
        "booking_requests": booking_requests,

    }
    return render(request, 'Staff/Technican_Dashboard.html', context)


# def bookedAppointment(request):
#     # booking_requests = BookAppointment.objects.filter(staff=request.user, confirmed=True)
    
#     # context = {
#     #     "booking_requests": booking_requests,

#     # }
#     # return render(request, 'Staff/technicianAppointmentHistory.html', context)

    



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

    context = {
        "booking_requests": booking_requests,
        "user_id": user_id,
    }
    return render(request, template_name, context)


   

#User Appointment History    
def appointmenthistory(request, user_id):
    
     return render(request, 'User_Profile_Management/appointmenthistory.html')   
 

 

    
#staff appointment History
def staffappointmentHistory(request, user_id):
    
    return render(request, 'Staff/technicianAppointmentHistory.html')



# hair-technician dashboard started
def HairStaffDashboard(request):
    return render(request, 'Staff/Technican_Dashboard.html')

def StaffEditProfile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_detail = user.userdetail

    if request.method == 'POST':
        # Process form if POST request
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        
        if 'address' in request.POST:  # Check if address is present in POST data
            user_detail.address = request.POST.get('address')
        if 'contact_number' in request.POST:  # Check if contact_number is present in POST data
            user_detail.contact_number = request.POST.get('contact_number')
        user_detail.save()
        
        messages.success(request, "User Details has been updated successfully.")
        return redirect('StaffEditProfile', user_id=user_id)  
    
    if "Update" in request.POST:
        
            profile = UserProfile.objects.get(user=user)
            profile.image =  request.FILES['save_update_image']
            profile.image.save()
            
            
            
            #print("IMAGEEEEEEEEEEEEEEEEE", image)
            # Saving user New profile
            users_profile = UserProfile.objects.get(user=user)
            users_profile.image = request.FILES['img']
            users_profile.save()
            messages.success(request, 'Profile Picture Changed.') 
    
    # If it's a GET request, render the edit profile page with the user data
    return render(request, 'Staff/StaffEditProfile.html', {'user': user, 'user_detail': user_detail})
 
