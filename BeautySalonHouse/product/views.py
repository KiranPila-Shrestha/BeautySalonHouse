from django.shortcuts import render, redirect, get_object_or_404
from . models import *
from .forms import *
from django.contrib import messages
from django.db.models import Sum, F


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


#for add to cart
def addtoCart(request, product_id):
    product = get_object_or_404(addProduct, id=product_id)
    
    #get or create the user cart
    user_cart,created = cart.objects.get_or_create(user=request.user)
    #check if the product is already in the cart
    cart_item, item_created = Cartitem.objects.get_or_create(cart=user_cart, product=product)
    
    #increae the quantity of cart if it is in cart
    if not item_created:
        cart_item.Quantity += 1
        cart_item.save()
        
    else:
        cart_item.Quantity = 1 # initial quantity set as 1 for first 
        cart_item.save()
        
    user_cart.total_amount = Cartitem.objects.filter(cart=user_cart).aggregate(total=Sum(F('product__productPrice') * F('Quantity')))['total']
    user_cart.save()
    
    messages.success(request, "Product has been added to the cart successfully.")
    return redirect ('productpage')
    
    
def cart_view(request):
    if request.method == 'POST': # create and get user cart
        user_cart, created = cart.objects.get_or_create(user= request.user)
    
    #iterate through product in the cart and quantity update
        for cart_item in Cartitem.objects.filter(cart=user_cart):
            new_quantity = int(request.POST.get(f"quantityInput-{cart_item.product.id}",1))
            
            #ensure the new quantity is within limit that is in stock
            new_quantity = max(1, min(new_quantity,cart_item.product.productStock))
            
            cart_item.Quantity = new_quantity
            cart_item.save()
        
        messages.success(request, "Cart updated.")
    
    user_cart,created = cart.objects.get_or_create(user=request.user)
    cart_item_set = user_cart.cartitem_set.all() # retrive all the cart items for user's cart
    
    context ={
        'cart_item_set':cart_item_set,
      '  user_cart': user_cart
    }

    return render(request, 'Inventory/addToCart.html', context)
    
# for update the cart
def update_cart(request):
    if request.method == 'POST':
        #print the post data request
        print("POST data:", request.POST)

        #Get or create the user's cart
        user_cart, created = cart.objects.get_or_create(user=request.user)
        
        print(user_cart)
        
        #initialize total
        total_amount =0
        
        if "delete" in request.POST:
            pId = request.POST.get('delete')
            item_delete = Cartitem.objects.filter(product_id = pId).first()
            print(item_delete)
            
            if item_delete:
                item_price = item_delete.product.productPrice
                print('item_price', item_price)
                
                #remove item from cart
                item_delete.delete()
                
                #for recalculation of total
                user_cart.total_amount -= item_price * item_delete.Quantity
                if user_cart.total_amount < 0:
                    user_cart.total_amount = 0
                    
                #save cart
                print('donee')
                user_cart.save()
        
        #iterate through product in cart and update quantites
        for cart_item in user_cart.cartitem_set.all():
            print('cart items:', cart_item.Quantity)
            #using product id to modify cart items
            cartID= str(cart_item.product.id)
            new_quantity = request.POST.get('Inputquantity-'+ cartID)
            print('Inputquantity-'+cartID)
            
            if new_quantity == None:
                old_quantity = cart_item.Quantity
                #update the cat item quantiy
                cart_item.Quantity = old_quantity
                cart_item.save()
            else:
                cart_item.Quantity = new_quantity
                cart_item.save()
                
            user_cart.update_total_amount()
            print("Total amount before saving:", user_cart.total_amount)
            user_cart.save()
            print("Total amount after saving:", user_cart.total_amount)
    return redirect('cartview')
    
def checkout(request):
   return render(request, 'Inventory/checkout.html')
#def addtoCart(request):
 #   return render(request, 'Inventory/addToCart.html')