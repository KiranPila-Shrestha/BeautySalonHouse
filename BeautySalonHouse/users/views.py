from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render,redirect, get_object_or_404
from .forms import *
from django.contrib import messages
# IMPORTING "update_session_auth_hash" to Change PASSWORD
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from users.models import *
from django.db import transaction
from django.contrib.auth.models import User

# SEND MAIL
from django.core.mail import send_mail
from django.conf import settings


# LOGIN
def loginUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None or user.is_superuser:
            login(request, user)
             
            return redirect('/')
        
        else:
            messages.info(request, 'Username or Password is incorrect')
        # get the UserVerify instance for the logged in user.
        # user_verify = UserVerify.objects.filter(user=user).first()    
        
        # Checking if that user is approved or not
        # if user is not None and user.is_superuser or(user is not None and user.groups.filter(name__in=['Owner', 'Tenant']).exists()):
        #     login(request, user)
        
        # elif user is not None and not user.groups.exists():
            
        #     messages.info(request, 'User is not approved.')

        # else:
        #     messages.info(request, 'Username or Password is incorrect')

    return render(request, 'login_register/login.html')


# REGISTER
def registerUser(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the username
            username = form.cleaned_data.get('username')
            # An atomic transaction guarantees that all operations within the block are treated as a single unit. 
            # If any operation fails, the entire transaction is rolled back, 
            # undoing all changes made within the block.
            with transaction.atomic():

                user = form.save()
                # saving user contact number and address
                user_details = UserDetail(user=user, address=request.POST.get('address'), contact_number=request.POST.get('contact'))
                user_details.save()  
                
                # Saving user default profile
                user_default_profile_picture = UserProfile(user=user)
                user_default_profile_picture.save()
                
                # Save profile image
                # if request.FILES:
                #     document = UserDocument(user=user, image=request.FILES['img'])
                #     document.save()
                # #     messages.success(request,"Account Created for " + username + " Please wait before we verify.")
                    
                
                # else:
                #     # Adding user to the Tenant group if they choose to become tenant 
                #     group = Group.objects.get(name="admin")
                #     user.groups.add(group)
                #     messages.success(request,"Account Created for " + username)
                    
                            
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
        # Process form data if it's a POST request
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        
        if 'address' in request.POST:  # Check if address is present in POST data
            user_detail.address = request.POST.get('address')
        if 'contact_number' in request.POST:  # Check if contact_number is present in POST data
            user_detail.contact_number = request.POST.get('contact_number')
        user_detail.save()
        
        messages.success(request, "User updated successfully.")
        return redirect('/', user_id=user_id)  # Redirect to the same page after form submission
    
    if "save_update_image" in request.POST:
            # Saving user New profile
            users_profile = UserProfile.objects.get(user=user)
            users_profile.image = request.FILES['img']
            users_profile.save()
            messages.success(request, 'Profile Picture Changed.') 
    
    # If it's a GET request, render the edit profile page with the user data
    return render(request, 'User_Profile_Management/EditProfile.html', {'user': user, 'user_detail': user_detail})

def ChangePassword(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_detail = user.userdetail
    if "ChangePassword" in request.POST:
            current_password = request.POST.get('currentPassword')
            new_password = request.POST.get('newPassword')
            confirm_new_password = request.POST.get('confirmPassword')
            print("CHANGE PASSWORD clicked")
            
            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
                print("error pass")
            else:
                if new_password != confirm_new_password:
                    messages.error(request, 'New password and confirm password do not match.')
                else:
                    # Change the user's password
                    request.user.set_password(new_password)
                    request.user.save()
                    messages.success(request, 'Password Changed')
                    # Updating the user's session to prevent logout
                    update_session_auth_hash(request, request.user)
    return render(request, 'Login_Register/Reset_Password/ChangePassword.html')



# def EditProfile(request, user_id):
#     user = get_object_or_404(User, id=user_id)
#     # user_profile_picture = UserProfilePicture.objects.filter(user=request.user).first()
#     # if user_profile_picture:
#     #     profile_picture = user_profile_picture.image.url

#     if request.method == 'POST':
#         if "save_details" in request.POST:
#             # UPDATING USER MODEL
#             user.first_name = request.POST.get('first_name')
#             user.last_name = request.POST.get('last_name')
#             user.email = request.POST.get('email')
#             user.save()
            
#             # UPDATING UserDetail MODEL
#             user_detail = user.userdetail
#             user_detail.address = request.POST.get('address')
#             user_detail.contact_number = request.POST.get('contact_number')
#             user_detail.save()
            
#             messages.success(request,"User updated successful.")
#         return render(request, 'User_Profile_Management/EditProfile.html')
    
    
    # if request.user.is_authenticated:
    #     current_user = User.objects.get(id=request.user.id)
    #     form = CreateUserForm(request.POST or None, instance = current_user)
    #     if form.is_valid():
    #         form.save()
    #         login(request, current_user)
    #         messages.success(request,("Your profile has been updated"))
    #         return redirect('/')
    #     return render(request, 'User_Profile_Management/EditProfile.html',{'form':form})
    # else:
    #     messages.success(request,("You must logged in..."))
    #     return redirect('/')
    
    # user_form = UserUpdateForm(instance=request.user)
    # Profile_form = ProfileUpadateForm(instance=request.user.UserProfile)
    
    # context = {
    #     'user_form': user_form,
    #     'Profile_form': Profile_form
    # }
    

def AdminDashBoard(request):
     return render(request, 'Admin_Page/AdminDashboard.html')
 
def send_email():
    subject = "This email from administrator"
    message =" Reset Your passsword"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = ["shresthakiran607@gmail.com"]
    
    send_mail(subject, message, from_email, recipient_list)