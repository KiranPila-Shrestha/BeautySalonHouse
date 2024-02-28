from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'landing_page/index.html')

def booking(request):
    return render(request, 'landing_page/booking.html')

def product(request):
    return render(request, 'landing_page/product.html')

def contact(request):
    return render(request, 'landing_page/Contact.html')