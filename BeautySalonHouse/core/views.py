from django.shortcuts import render
from Appointment.models import *

# Create your views here.
def index(request):
    return render(request, 'landing_page/index.html')


def product(request):
    return render(request, 'landing_page/product.html')

def contact(request):
    return render(request, 'landing_page/Contact.html')


def service(request):
    feedback = AppointmentFeedback.objects.all()
    
    context= {
        'feedback' : feedback
    }
    
    return render(request, 'landing_page/service.html', context)

def hairservice(request):
    return render(request, 'landing_page/Hairservice.html')

def makeupservice(request):
    return render(request, 'landing_page/Makeupservice.html')

def nailservice(request):
    return render(request, 'landing_page/nailservice.html')

def skinservice(request):
    return render(request, 'landing_page/skinservice.html')