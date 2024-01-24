from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render,redirect, get_object_or_404
from .forms import *
from django.contrib import messages
# IMPORTING "update_session_auth_hash" to Change PASSWORD
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from users.models import *
from django.db import transaction
from django.contrib.auth.models import User,Group

# SEND MAIL
from django.core.mail import send_mail


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
                # user_default_profile_picture = UserProfilePicture(user=user)
                # user_default_profile_picture.save()
                
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