from django.forms import ModelForm, ChoiceField, Select, MultipleChoiceField
from django.contrib.auth.forms import User
from django import forms
from .models import *


class productForm(ModelForm):
    class Meta:
        model = addProduct
        fields = ['productName', 'productCategory', 'productBrand','productDescription','productPrice', 'productStock']