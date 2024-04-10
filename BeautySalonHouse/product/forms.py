from django.forms import ModelForm, ChoiceField, Select, MultipleChoiceField
from django.contrib.auth.forms import User
from django import forms
from .models import *


class productForm(ModelForm):
    productName = forms.CharField(
        label='Product Name',
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Product Name', 'class': 'border-2 border-gray-400 rounded-xl p-2 mt-2 mb-5 w-[25rem] bg-gray-100 '})
    )
    productBrand = forms.CharField(
        label='Product Brand',
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Product Brand', 'class': 'border-2 border-gray-400 rounded-xl p-2 mt-2 mb-5 w-[25rem] bg-gray-100 '})
    )

    productPrice = forms.FloatField(
        label='Product Price',
        widget=forms.NumberInput(attrs={'placeholder': 'Product Price', 'class': 'border-2 border-gray-400 rounded-xl p-2 mt-2 mb-5 w-[25rem] bg-gray-100', 'min': 0, 'step': 0.1})
    )

    productDescription = forms.CharField(
        label='Product Description',
        max_length=100,
        widget=forms.Textarea(attrs={'placeholder': 'Product Description', 'class': 'border-2 border-gray-400 rounded-xl p-2 mt-2 mb-5 w-[25rem] bg-gray-100', 'rows': 4, 'cols': 40})
    )

    productStock = forms.IntegerField(
        label='Product Stock',
        widget=forms.NumberInput(attrs={'placeholder': 'Product Stock', 'class': 'border-2 border-gray-400 rounded-xl p-2 mt-2 mb-5 w-[25rem] bg-gray-100', 'min': 0, 'step': 1})
    )

    productCategory = ChoiceField(
        choices=productCategoryChoice,
        widget=Select(attrs={'class': 'border-2 border-gray-400 rounded-xl p-2 mt-2 mb-5 w-[25rem] bg-gray-100'}),
        required=True
    )

    class Meta:
        model = addProduct
        fields = ['productName', 'productCategory', 'productBrand', 'productDescription', 'productPrice', 'productStock']
       

class editproductForm(ModelForm):
    productName = forms.CharField(
        label='Product Name',
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Product Name', 'class': 'border-2 border-gray-400 rounded-xl p-2 mt-2 mb-5 w-[25rem] bg-gray-100 '})
    )
    productBrand = forms.CharField(
        label='Product Brand',
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Product Brand', 'class': 'border-2 border-gray-400 rounded-xl p-2 mt-2 mb-5 w-[25rem] bg-gray-100 '})
    )

    productPrice = forms.FloatField(
        label='Product Price',
        widget=forms.NumberInput(attrs={'placeholder': 'Product Price', 'class': 'border-2 border-gray-400 rounded-xl p-2 mt-2 mb-5 w-[25rem] bg-gray-100', 'min': 0, 'step': 0.1})
    )

    productDescription = forms.CharField(
        label='Product Description',
        max_length=100,
        widget=forms.Textarea(attrs={'placeholder': 'Product Description', 'class': 'border-2 border-gray-400 rounded-xl p-2 mt-2 mb-5 w-[25rem] bg-gray-100', 'rows': 4, 'cols': 40})
    )

    productStock = forms.IntegerField(
        label='Product Stock',
        widget=forms.NumberInput(attrs={'placeholder': 'Product Stock', 'class': 'border-2 border-gray-400 rounded-xl p-2 mt-2 mb-5 w-[25rem] bg-gray-100', 'min': 0, 'step': 1})
    )

    productCategory = ChoiceField(
        choices=productCategoryChoice,
        widget=Select(attrs={'class': 'border-2 border-gray-400 rounded-xl p-2 mt-2 mb-5 w-[25rem] bg-gray-100'}),
        required=True
    )

    class Meta:
        model = addProduct
        fields = ['productName', 'productCategory', 'productBrand', 'productDescription', 'productPrice', 'productStock']