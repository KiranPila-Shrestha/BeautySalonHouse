from django.shortcuts import render, redirect, get_object_or_404
from . models import *
from django.contrib import messages

# Create your views here.
def product_add(request):
    productList = addProduct.objects.all()
    
    context = {
        'productList' : productList
    }

    return render(request, '')