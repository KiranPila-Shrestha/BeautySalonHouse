from django.shortcuts import render
from Appointment.models import *
from .forms import ContactForm
from django.core.mail import send_mail
from django.contrib import messages
import sweetify
# Create your views here.
def index(request):
    return render(request, 'landing_page/index.html')


def product(request):
    return render(request, 'landing_page/product.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            recipient_email = 'pilashrestha366@gmail.com'  #admin mail
            
            # Send email
            send_mail(
                f'New message from {name}',
                f'Name: {name}\nEmail: {email}\n\nMessage:\n{message}',
                email,
                [recipient_email],
                fail_silently=False,
            )
            sweetify.success(request, " Form has been submitted")  # Display a success page or redirect as needed
    else:
        form = ContactForm()
    return render(request, 'landing_page/Contact.html')


def service(request):
    feedback = AppointmentFeedback.objects.all()
    
    context= {
        'feedback' : feedback
    }
    
    return render(request, 'landing_page/service.html', context)

def hairservice(request):
    hairfeedback = []
    bookedAppoinment = BookAppointment.objects.filter(service='Hair service')
    if bookedAppoinment and bookedAppoinment is not None:
        # print("bookedAppoinmentbookedAppoinment", bookedAppoinment)
        for appoinments in bookedAppoinment:
            print("appoinments", appoinments)
            hairfeedbacks = AppointmentFeedback.objects.filter(appointment=appoinments)
            if hairfeedbacks is not None:
                for hair in hairfeedbacks:
                    hairfeedback.append(hair)
    print("hairfeedbackhairfeedbackhairfeedback", hairfeedback)
    context = {
        "hairfeedback" : hairfeedback
    }    
    
    return render(request, 'landing_page/Hairservice.html', context)



def makeupservice(request):
    makeup_feedback = []

    # Retrieve appointments for the "Make-up" service
    makeup_appointments = BookAppointment.objects.filter(service='Make-up')
    print(makeup_appointments)

    # Iterate over the retrieved appointments
    for appointment in makeup_appointments:
        print("appointment222222", appointment.id)
        # Retrieve associated makeup feedback for each appointment
        makeup_feedbacks = AppointmentFeedback.objects.filter(appointment_id=appointment)
        print("makeup_feedbacks222222222", makeup_feedbacks)
        # Add the retrieved feedback to the makeup_feedback list
        for feedback in makeup_feedbacks:
            makeup_feedback.append(feedback)
    print("makeup_feedbackmakeup_feedback", makeup_feedback)
    context = {
        "makeup_feedback": makeup_feedback
    }    
    
    return render(request, 'landing_page/Makeupservice.html', context)

def nailservice(request):
    nailfeedback = []
    bookedAppoinment = BookAppointment.objects.filter(service='Nail Service')
    print(bookedAppoinment)
    if bookedAppoinment and bookedAppoinment is not None:
        # print("bookedAppoinmentbookedAppoinment", bookedAppoinment)
        for appoinments in bookedAppoinment:
            nailfeedbacks = AppointmentFeedback.objects.filter(appointment=appoinments)
            if nailfeedbacks is not None:
                for nail in nailfeedbacks:
                   nailfeedback.append(nail)
    print("Nail ServiceNail Service", nailfeedback)
    context = {
        "nailfeedback" : nailfeedback
    }    
    
    
    return render(request, 'landing_page/nailservice.html', context)

def skinservice(request):
    skinfeedback = []
    bookedAppoinment = BookAppointment.objects.filter(service='Skin Care')
    print(bookedAppoinment)
    if bookedAppoinment and bookedAppoinment is not None:
        # print("bookedAppoinmentbookedAppoinment", bookedAppoinment)
        for appoinments in bookedAppoinment:
            skinfeedbacks = AppointmentFeedback.objects.filter(appointment=appoinments)
            if skinfeedbacks is not None:
                for skin in skinfeedbacks:
                   skinfeedback.append(skin)
    print("akin Service", skinfeedback)
    context = {
        "skinfeedback" : skinfeedback
    }    
    
    return render(request, 'landing_page/skinservice.html', context)

def errorpage(request):
    return render(request, '404page.html')


def error_404(request, exception):
    return render(request, '404page.html', status=404)
 
def error_500(request):
    return render (request, '404page.html', status=500)