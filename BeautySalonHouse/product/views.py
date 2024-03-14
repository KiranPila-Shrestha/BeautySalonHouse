from django.shortcuts import render, redirect, get_object_or_404
from . models import *
from .forms import *
from django.contrib import messages

# Create your views here.
def product_add_market(request):
    productList = addProduct.objects.all()
    # productImage = productImage.objects.filter(addProduct=productList)
    
    context = {
        'productList' : productList,
         'productCategoryChoice': productCategoryChoice,
        #  'productImage' : productImage,
    }

    return render(request, 'Inventory/product.html', context)



# for adding product admin

def AddProduct(request):
    #getting data from form.py
    if request.method == 'POST':
        form = productForm(request.POST, request.FILES)
        
        if form.is_valid():
            instance = form.save(commit=False) #false helps to not to save the form
            instance.user = request.user
            
            #now handling product category feild
            select_category = form.cleaned_data['productCategory']
            
            #now set the selected category
            instance.productCategory = select_category
            
            instance.save()
            
            #step 2 image handling of product
            product_image = request.FILES.getlist('productImage')
            for image in product_image:
                productImage.objects.create(addProduct=instance, image=image)
                print('ok')
                
            messages.success(request, "Product added successfully")
            return redirect('addproduct') # redirect the page after succesfull adding 
        else:
            print("please add")
            print(form.errors)
    else:
        form = productForm()
        
    context = {
        'form':form,
        'productCategoryChoice': productCategoryChoice,
    }       
    return render(request, 'Inventory/Addproduct.html', context)
    print('done')

# Product description form

def productdetail(request, product_id):
    productlist = addProduct.objects.all()
    
    # to get details
    productdetail = get_object_or_404(addProduct, id=product_id)
    
    
    #to get image of product
    productdetailImage = get_object_or_404(addProduct, id=product_id)
    
    product_image = productImage.objects.filter(addProduct=productdetailImage)

    
    context ={
        'productlist': productlist,
        'productdetail': productdetail,
        'productdetailImage': productdetailImage,
        'product_image':product_image,
    }
    
    return render(request, 'Inventory/productdetail.html', context)





def productlist(request):
    if request.method == 'POST':
        product_id = request.POST.get("product_id")  # Retrieve product ID from the form data
        if product_id:
            product = get_object_or_404(addProduct, id=product_id)
            
            if 'delete' in request.POST:
                product.delete()
                # Redirect or return a success message
                print('Product deleted successfully')
                return redirect('productlist')
    
    products = addProduct.objects.all()
    context = {'products': products}
    return render(request, 'Inventory/Productlisting.html', context)

def addtoCart(request):
    return render(request, 'Inventory/addToCart.html')

def checkout(request):
    return render(request, 'Inventory/checkout.html')