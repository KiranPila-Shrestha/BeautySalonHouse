from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render,redirect, get_object_or_404
from .forms import *

from datetime import datetime
from django.utils import timezone
from django.contrib import messages
# IMPORTING "update_session_auth_hash" to Change PASSWORD
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from users.models import *
from django.db import transaction
from django.contrib.auth.models import User

# SEND MAIL
from django.core.mail import send_mail
from django.conf import settings
import sweetify

##appointment models
from Appointment.models import *
##product modeks
from product.models import *
from django.db.models import Sum

# LOGIN
def loginUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # if user.userdetail.has_blocked == True:
            #     sweetify.error(request, 'Your account has been blocked. Please contact to admin.')
            # else:
            login(request, user)
            sweetify.success(request, "Successfully Login. Welcome to our site.")
            return redirect('/')
        
        else:
            sweetify.info(request, 'Username or Password is invalid.')
        

    return render(request, 'login_register/login.html')


# REGISTER
def registerUser(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the username
            username = form.cleaned_data.get('username')
            # If any operation fails, the entire transaction is rolled back, undoing all changes made within the block.
            with transaction.atomic():

                user = form.save()
                # saving user contact number and address
                user_details = UserDetail(user=user, address=request.POST.get('address'), contact_number=request.POST.get('contact'))
                user_details.save()  
                
                # Saving user default profile
                user_default_profile_picture = UserProfile(user=user)
                user_default_profile_picture.save()
            sweetify.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
        else:
            # Display error message
            sweetify.error(request, 'Registration failed. Please correct the errors below.')
            

                       
            return redirect('login')
            
    context = {'form': form,}
    return render(request, 'login_register/register.html', context)


# logout user
def logoutUser(request):
    
    logout(request)
    return redirect('login')

##EditProfile user
def EditProfile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_detail = user.userdetail

    if request.method == 'POST':
        if "user" in request.POST:
            username = request.POST.get('user')
            user = User.objects.get(username=username)
            print(user)
            
        if "Update" in request.POST:
             #update user detail
            print("updaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaateeeeeeeeee")
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.save()
            print(user)
           
        #updating additional details
        
        if 'address' in request.POST:  # Check if address is present in POST data
            user_detail.address = request.POST.get('address')
        if 'contact_number' in request.POST:  # Check if contact_number is present in POST data
            user_detail.contact_number = request.POST.get('contact_number')
        user_detail.save()
        sweetify.success(request, "User Details has been updated successfully.")
        
        
        
        if 'saveImage' in request.POST:
            # Check if an image was uploaded
            if 'save_update_image' in request.FILES:
                print("image ayoooooooooo")
                profile = UserProfile.objects.get(user=user)
                profile.image = request.FILES['save_update_image']
                profile.save()
                sweetify.success(request, 'Profile Picture Changed.')
            
        
            # return redirect('EditProfile', user_id=user_id)  
        else:
            messages.error(request, 'No image uploaded.')
    
       
        
        if "deleteImage" in request.POST:
            users_profile = UserProfile.objects.get(user=user)
            users_profile.delete()
            #saving default
            user_default_profile = UserProfile(user=user)
            user_default_profile.save()
            messages.success(request, 'Profile Picture Updated.')
        #print("IMAGEEEEEEEEEEEEEEEEE", image)


    # If it's a GET request, render the edit profile page with the user data
    return render(request, 'User_Profile_Management/EditProfile.html', {'user': user, 'user_detail': user_detail})

#  Change-password function part start
def ChangePassword(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_detail = user.userdetail
    if "ChangePassword" in request.POST:
            current_password = request.POST.get('currentPassword')
            new_password = request.POST.get('newPassword')
            confirm_new_password = request.POST.get('confirmPassword')
            print("CHANGE PASSWORD clicked")
            
            if not request.user.check_password(current_password):
                sweetify.error(request, 'Current password is incorrect.')
                print("error pass")
            else:
                if new_password != confirm_new_password:
                    sweetify.error(request, 'New password and confirm password do not match.')
                else:
                    # Change the user's password
                    request.user.set_password(new_password)
                    request.user.save()
                    sweetify.success(request, 'Password Changed')
                    # Updating the user's session to prevent logout
                    update_session_auth_hash(request, request.user)
    return render(request, 'Login_Register/Reset_Password/ChangePassword.html')

#sending Mail Part
def send_email():
    subject = "This email from administrator"
    message =" Reset Your passsword"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = ["shresthakiran607@gmail.com"]
    
    send_mail(subject, message, from_email, recipient_list)
    
#Admin DashBoard Part start  

def AdminDashBoard(request):
    form = CreateUserForm()
    if request.method == 'POST' and "addStaff" in request.POST:
        print("STEP1")
        form = CreateUserForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the username
            username = form.cleaned_data.get('username')
            # If any operation fails, the entire transaction is rolled back, undoing all changes made within the block.
            with transaction.atomic():

                user = form.save()
                # saving user contact number and address
                user_details = UserDetail(user=user, address=request.POST.get('address'), contact_number=request.POST.get('contact'),
                                user_type = request.POST.get('user_type'))
                user_details.save() 
                print("111") 
                
                if "user_type" in request.POST:
                    userType = request.POST.get('user_type')
                    group, create = Group.objects.get_or_create(name= userType)
                    user.groups.add(group)
                    print("555")
                    
                    # MESSAGE
                    
                # Saving user default profile
                user_default_profile_picture = UserProfile(user=user)
                user_default_profile_picture.save()
                
                #send mail
                user_email = user.email
                user_type = request.POST.get('user_type')
                send_mail("Welcome to our salon","You have been assigned as {user_type}","pilashrestha366@gmail.com",[user_email],fail_silently=False)
                
                sweetify.success(request, " Staff has been added Successfully")
        else:
            sweetify.error(request, "Error occur while staff adding.")
                
                
            
    
    return render(request, 'Admin_Page/AdminDashboard.html')



###for user details view by admin

def is_superuser(user):
    return user.is_superuser


@login_required(login_url='login')
@user_passes_test(is_superuser)

def userdetail_admin(request):
    if request.method == 'POST':
        if 'block' in request.POST or 'unblock' in request.POST:
            print("clickkkk")
            username = request.POST.get("user")
            print(username)
            try:
                user = User.objects.get(username=username)
                user_detail = UserDetail.objects.get(user=user)
                if 'block' in request.POST:
                    user_detail.hasUserBlocked= True
                    sweetify.success(request, 'User blocked successfully')
                elif 'unblock' in request.POST:
                    user_detail.hasUserBlocked = False
                    sweetify.success(request, 'User unblocked successfully')
                user_detail.save()
            except User.DoesNotExist:
                sweetify.error(request, 'User does not exist')
        elif 'userdelete' in request.POST:
            username = request.POST.get('username')
            try:
                user = User.objects.get(username=username)
                user.delete()
                sweetify.success(request, 'User deleted successfully')
                return redirect('useradmin')
            except User.DoesNotExist:
                sweetify.error(request, 'User does not exist')
            
            
            return redirect('useradmin')
    requestedUserType = UserDetail.objects.all()
    requested_users = UserDetail.objects.filter(user_type='customer').count()
    print(requested_users)
    
    allUserlogin = User.objects.filter(is_superuser=False)
    # User.objects.filter(groups__name__in=["Hair Technician", "Laser Skin", "Nail Technician", "Makeup Artist"] )
    
    total_hairtechnician = User.objects.filter(groups__name='Hair Technician').exclude(is_superuser=True).count()
    total_skintechnician = User.objects.filter(groups__name='Laser Skin').exclude(is_superuser=True).count()
    total_nailtechnician = User.objects.filter(groups__name='Nail Technician').exclude(is_superuser=True).count()
    total_makeuptechnician = User.objects.filter(groups__name='Makeup Artist').exclude(is_superuser=True).count()
    print("sakjgdhsagdjhsdghg",total_makeuptechnician)
    
  

    context = {
        'requestedUserType':  requestedUserType,
        'total_hairtechnician':total_hairtechnician,
        'total_skintechnician': total_skintechnician,
        'total_nailtechnician': total_nailtechnician,
        
        'total_makeuptechnician':  total_makeuptechnician,
        'allUserlogin':allUserlogin,
        'requested_users':requested_users,
    }

    return render(request, 'Admin_Page/Userdetails.html', context)


###Data visualization admin part

def adminchart(request):
    staff_data = {}
    user_types = UserDetail.objects.values_list('user_type', flat=True)
    

    # Count available of each user type
    user_type_counts = {}
    for user_type in user_types:
        user_type_counts[user_type] = user_type_counts.get(user_type, 0) + 1
    
    # Prepare data for Chart.js (for user type distribution)
    labels = list(user_type_counts.keys())
    data = list(user_type_counts.values())
    table_data = [(label, count) for label, count in user_type_counts.items()]
    
    #appointment  staff having view starts
    
    # Group appointments by status
    appointment_statuses = BookAppointment.objects.values('status').annotate(count=models.Count('id'))
    print(appointment_statuses)
    
    # Prepare data for staff appointment distribution 
    appointment_status_data = {status['status']: status['count'] for status in appointment_statuses}
    print( appointment_status_data)
    
  
    # Retrieve staff data for appointment distribution
    staff_appointments = BookAppointment.objects.values('staff', 'status').annotate(count=models.Count('id'))
    print(staff_appointments)
    
    
    # Fetch users with a specific user type
    requested_users = UserDetail.objects.filter(user_type='customer')
    
    # Fetch users belonging to specific groups
    all_user_login = User.objects.filter(groups__name__in=["Hair Technician", "Laser Skin", "Nail Technician", "Makeup Artist"])
    
    for appointment in staff_appointments:
        staff = appointment['staff']
        status = appointment['status']
        count = appointment['count']
        
        print(f"Staff: {staff},  Status: {status}, Count: {count}") 
     
        # Initialize staff data if not already present
        if staff not in staff_data:
            staff_data[staff] = {'Pending': 0, 'Confirm': 0, 'Canceled': 0, 'completed': 0}
        if status not in staff_data[staff]:
            staff_data[staff][status] = 0
    
        # Update staff data with the count for the corresponding status
        staff_data[staff][status] = count
        
        print("staff: {staff_data}")
        
        #fro service used by user customer
        
          # Fetch service distribution data
    service_distribution = BookAppointment.objects.values('service').annotate(count=models.Count('id'))
    service_data = {service['service']: service['count'] for service in service_distribution}
    
    print(service_data)
    
    products = addProduct.objects.all()
    product_names = [product.productName for product in products]
    product_stock = [product.productStock for product in products]
    print('name', product_names)
    print('stock', product_stock)
    
    
   # Prepare data for visualization
    order_statuses = ['Pending', 'Completed', 'Cancelled']
    order_counts = [
    orderplaced.objects.filter(status='Pending').count(),
    orderplaced.objects.filter(status='Completed').count(),
    orderplaced.objects.filter(status='Cancelled').count()
]

# Create order_data list of dictionaries
    order_data = [{'status': status, 'count': count} for status, count in zip(order_statuses, order_counts)]

    
    context = {
        'labels': labels,
        'data': data,
        'table_data': table_data,
        'appointment_status_data': appointment_status_data,
        'staff_data': staff_data,
        'requested_users': requested_users,
        'all_user_login': all_user_login,
        'service_data': service_data,
        'product_names': product_names,
        'product_stock': product_stock,
        
        'order_statuses': order_statuses,
        'order_counts': order_counts,
        'order_data': order_data ,
    }
    
    
    return render(request, 'Admin_Page/ChartAdmin.html', context)