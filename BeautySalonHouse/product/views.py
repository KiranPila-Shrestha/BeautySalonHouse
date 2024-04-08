from django.shortcuts import render, redirect, get_object_or_404
from . models import *
from .forms import *
from django.contrib import messages
from django.db.models import Sum, F
import json
import requests
from django.http import HttpResponse
from django.db import transaction
from users.models import *
import sweetify 
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
                
            sweetify.success(request, "Product added successfully")
            return redirect('addproduct') # redirect the page after succesfull adding 
        else:
            sweetify.error(request, "Unable to add product, Fill all required feilds.")
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
    productCategoryChoice = addProduct.objects.values_list('productCategory', flat=True).distinct()
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
    context = {'products': products,
               'productCategoryChoice': productCategoryChoice,}
    return render(request, 'Inventory/Productlisting.html', context)


#for add to cart


def addtoCart(request, product_id):
  # Check if the user is authenticated and is of type 'customer'
    if request.user.is_authenticated:
        try:
            user_detail = request.user.userdetail
            if user_detail.user_type != 'customer':
                sweetify.error(request, 'Authentication Error', text='You must be logged in as a customer to add items to the cart.')
                return redirect('productpage')  # Redirect to login page or any other page as per your requirement
        except UserDetail.DoesNotExist:
            sweetify.error(request, 'User Detail Error', text='User detail does not exist.')
            return redirect('productpage')  # Redirect to login page or any other page as per your requirement
    else:
        sweetify.error(request, 'Authentication Error', text='You must be logged in as a customer to add items to the cart.')
        return redirect('productpage')  # Redirect to login page or any other page as per your requirement
    
    
    product = get_object_or_404(addProduct, id=product_id)
    

    #get or create the user cart
    user_cart,created = cart.objects.get_or_create(user=request.user)
    #check if the product is already in the cart
    cart_item, item_created = Cartitem.objects.get_or_create(cart=user_cart, product=product)
    
    productQuantity = product.productStock
    cartQuantity = cart_item.Quantity
    
    if not item_created and cartQuantity == productQuantity:
        sweetify.error(request, "Maximum quantity reached !!")
        return redirect ('productpage')
    
    
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
# def update_cart(request):
#     if request.method == 'POST':
#         #print the post data request
#         print("POST data:", request.POST)

#         #Get or create the user's cart
#         user_cart, created = cart.objects.get_or_create(user=request.user)
        
#         print(user_cart)
#             # Initialize success messages list
#         removal_success_messages = []
#         update_success_messages = []
        
#         #initialize total
#         total_amount =0
        
#         if "delete" in request.POST:
#             pId = request.POST.get('delete')
#             item_delete = Cartitem.objects.filter(product_id = pId).first()
#             print(item_delete)
            
            
#             if item_delete:
#                 item_price = item_delete.product.productPrice
#                 print('item_price', item_price)
                
#                 #remove item from cart
#                 item_delete.delete()
                
#                 #for recalculation of total
#                 user_cart.total_amount -= item_price * item_delete.Quantity
#                 if user_cart.total_amount < 0:
#                     user_cart.total_amount = 0
#                     print( user_cart.total_amount)
                    
#                 #save cart
#                 print('donee')
#                 user_cart.save()
#             # Add success message
#                 removal_success_messages.append("Cart item has been removed successfully.")
        
#         #iterate through product in cart and update quantites
#         for cart_item in user_cart.cartitem_set.all():
#             print('cart items:', cart_item.Quantity)
#             #using product id to modify cart items
#             cartID= str(cart_item.product.id)
#             new_quantity = request.POST.get('Inputquantity-'+ cartID)
#             print('Inputquantity-'+cartID)
            
#             if new_quantity == None:
#                 old_quantity = cart_item.Quantity
#                 #update the cat item quantiy
#                 cart_item.Quantity = old_quantity
#                 cart_item.save()
#             else:
#                 cart_item.Quantity = new_quantity
#                 cart_item.save()
                
           
    
#             user_cart.update_total_amount()
#             print("Total amount before saving:", user_cart.total_amount)
#             user_cart.save()
#             print("Total amount after saving:", user_cart.total_amount)
            
#                   # Add success message
#             update_success_messages.append.append("Cart item has been updated successfully.")
#             print("Success messages:", update_success_messages)
    
#          # Add success messages to Django messages framework
#         for message in removal_success_messages:
#             sweetify.success(request, message + " (Removal)")
        
#         for message in update_success_messages:
#             sweetify.success(request, message + " (Update)")
    
#     return redirect('cartview')
    
def update_cart(request):
    if request.method == 'POST':
        # Get or create the user's cart
        user_cart, created = cart.objects.get_or_create(user=request.user)
        
        # Initialize success messages list
        removal_success_messages = []
        update_success_messages = []
        
        # Check for item deletion
        if "delete" in request.POST:
            pId = request.POST.get('delete')
            item_delete = Cartitem.objects.filter(product_id=pId).first()
            if item_delete:
                item_price = item_delete.product.productPrice
                item_delete.delete()
                user_cart.total_amount -= item_price * item_delete.Quantity
                if user_cart.total_amount < 0:
                    user_cart.total_amount = 0
                user_cart.save()
                # Add success message for item removal
                removal_success_messages.append("Cart item has been removed successfully.")
        
        # Iterate through products in cart and update quantities
        for cart_item in user_cart.cartitem_set.all():
            cartID = str(cart_item.product.id)
            new_quantity = request.POST.get('Inputquantity-' + cartID)
            if new_quantity is None:
                old_quantity = cart_item.Quantity
                cart_item.Quantity = old_quantity
                cart_item.save()
            else:
                cart_item.Quantity = new_quantity
                cart_item.save()
            user_cart.update_total_amount()
            user_cart.save()
            # Add success message for item update
            update_success_messages.append("Cart item has been updated successfully.")
    
        # Add success messages to Django messages framework
        for message in removal_success_messages:
            sweetify.success(request, message + " (Removal)")
        
        for message in update_success_messages:
            sweetify.success(request, message + " (Update)")
    
    return redirect('cartview')


    
def checkoutpage(request):
    if request.method == "POST":
        if "saveDetails" in request.POST:
            new_address = request.POST.get('address')
            new_number = request.POST.get('phone_number')
            user_cart, created = cart.objects.get_or_create(user=request.user)
            user_cart.new_address = new_address
            user_cart.new_number = new_number
            user_cart.save()
    cartItems = cart.objects.filter(user=request.user)
    user_detail = UserDetail.objects.get(user=request.user)  # or UserDetail.objects.get(user_id=user_id)
    reward_points = user_detail.reward_points
    context= {
        'cartItems' : cartItems,
        'reward_points':reward_points,
    }
    return render(request, 'Inventory/checkout.html', context)


def checkout(request):        
    return render(request, 'Inventory/checkout.html')


# #paymenttt

def initkhalti(request):
    print("YAAAAAAAAAAAAAAAAAAAAAAAAAA AAYO")
    user = request.user.username
    userinformation = request.user
    contact = userinformation.userdetail.contact_number
    email = userinformation.email

    url = "https://a.khalti.com/api/v2/epayment/initiate/"
     
    
    return_url = request.POST.get('return_url')
    purchase_order_id = request.POST.get('purchase_order_id')
    stramount = request.POST.get('amount')
    amount = float(stramount)
    print(amount)

    payload = json.dumps({
        "return_url": return_url,
        "website_url": "http://127.0.0.1:9999",
        "amount": amount,
        "purchase_order_id": purchase_order_id,
        "purchase_order_name": "test",
        "customer_info": {
            "name": user,
            "email": email,
            "phone": contact,
        }
    })
    headers = {
         'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'key 38f188dd685e4006b1a2015725fa77f5', 
        
    }
    try:
        
        response = requests.request("POST", url, headers=headers, data=payload)
        new_res = json.loads(response.text)

        if new_res['payment_url']:
            return redirect(new_res['payment_url'])
            return redirect("paymentSucessful")
        
        else:
            messages.error(request, "Error while processing.")
            return redirect("cartview")
    except KeyError:
        
        pass
        
        # ERROR PAGE BANAUNE
        
        # return redirect("error") 
     
     
#  for khalti
def verifyKhalti(request):
    url = "https://a.khalti.com/api/v2/epayment/lookup/"
    if request.method == 'GET':
        headers = {
             'accept': 'application/json',
            'Authorization': 'key 38f188dd685e4006b1a2015725fa77f5', #10e9db6041cf49bc91884313102e3173
            'Content-Type': 'application/json',
        }
        pidx = request.GET.get('pidx')
        
        payload = json.dumps({
        'pidx': pidx
        })
        
        res = requests.request('POST',url,headers=headers,data=payload)
        
        new_res = json.loads(res.text)
        print("new_res",new_res)
        if new_res['status'] == 'Completed':
            print("SUCCESS PAYMENT")
            Buyeruser = request.user
            checkout_total_amount = int(new_res['total_amount'])
            cartInstance = get_object_or_404(cart, user=Buyeruser)
            print("cartcartcartcartcartcartcartcartcartcartcartcartcartcartcartcart: ", cartInstance)
            cart_itemsInstance = Cartitem.objects.filter(cart = cartInstance)

            with transaction.atomic():
                order = orderplaced.objects.create(
                    Buyeruser = Buyeruser,
                    total_amount = cartInstance.total_amount,
                    order_contact_number = cartInstance.new_number,
                    order_address =cartInstance.new_address,
                    status = 'Pending'
                )
                
                rewardPoint = int(Buyeruser.userdetail.reward_points)
                cartTotalAmount = int(cartInstance.total_amount)
                1000 == 1000  
                if checkout_total_amount == cartTotalAmount: # update the rewaed if not used
                    print("same amount")
                    user_detail = UserDetail.objects.get(user = Buyeruser)  
                    user_detail.reward_points += 1
                    reward_point_used = 0
                    user_detail.save()
                else:
                    print("Different amount")
                    user_detail = UserDetail.objects.get(user = Buyeruser)  
                    user_detail.reward_points = 1
                    user_detail.save()

                    reward_point_used = rewardPoint
                
                for cart_item in cart_itemsInstance:
                    product = cart_item.product
                    quantity = cart_item.Quantity
                    total_amount_product = product.productPrice * quantity
                    
                    orderhistoryDetails.objects.create(
                        order_for = order,
                        product = product,
                        quantity = quantity,
                        total_amount_product =total_amount_product
                    )
            
                order.rewardpoint = reward_point_used
                order.save()
                cart_itemsInstance.delete()
                cartInstance.delete()
                return render(request, 'payment/paymentsuccess.html')
        else:
            return redirect('error')
    else:
        pass
        # return redirect('error')
            
    return render(request, 'payment/paymentsuccess.html')


def paymentSuccess(request):
    return render(request, 'payment/paymentsuccess.html')

#for payment history 
def paymentHistory(request):
    orderDetails = []
    allOrderDetails = []
    
    
    orderPaymentHistory = orderplaced.objects.filter(Buyeruser=request.user)
    allOrderPaymentHistory = orderplaced.objects.all()
    for order in allOrderPaymentHistory:
        orderDetail = orderhistoryDetails.objects.filter(order_for=order)
        allOrderDetails.append(orderDetail)
    
    for order in orderPaymentHistory:
        orderDetail = orderhistoryDetails.objects.filter(order_for=order)
        orderDetails.append(orderDetail)
        
    if request.method == 'POST':
        if "confirmOrder" in request.POST:
            orderID = request.POST.get("orderID")
            orderHistory = orderhistoryDetails.objects.get(pk=orderID)
            orderHistory.status = "Completed"
            sweetify.success(request, "Order updated successfully!!")
            
        elif "cancelOrder" in request.POST:
            orderID = request.POST.get("orderID")
            orderHistory = orderhistoryDetails.objects.get(pk=orderID)
            orderHistory.status = "Rejected"
            sweetify.success(request, "Order updated successfully!!")

    context = {
        'orderPaymentHistory' : orderPaymentHistory,
        'orderDetails' : orderDetails,
        'allOrderDetails' : allOrderDetails,
        'allOrderPaymentHistory' : allOrderPaymentHistory
    }

    return render(request, 'payment/paymentHistory.html', context)

#for admin edit product
# def edit_product(request, product_id):
#     # Retrieve the product instance
#     product_instance = get_object_or_404(addProduct, pk=product_id)
    
#     if request.method == 'POST':
#         # If it's a POST request, process the form data
#         form = editProductForm(request.POST, instance=product_instance)
#         if form.is_valid():
#             form.save()
            
#             new_images = request.FILES.getlist('productImage')
            
#             # Get the list of existing images
#             old_images = product_instance.images.all()
            
#             # Delete old images not included in the new set
            
#             # Handle product images
#             if new_images:
#                 for old_image in old_images:
#                     if old_image.image not in new_images:
#                         old_image.delete()

#                 for uploaded_file in new_images:
#                     productImage.objects.create(addProducts=product_instance, image=uploaded_file)
            
#             messages.success(request, "Successfully edited product")
#             return redirect('productDetail', product_id=product_instance.id)
#     else:
#         # If it's not a POST request, populate the form with instance data
#         form = editProductForm(instance=product_instance)
    
#     context = {
#         'form': form,
#         'product_instance': product_instance,
        
#     }
#     return render(request, 'marketplace/editProduct.html', context)



def edit_product(request, product_id=None):
    # If product_id is provided, fetch the instance of the product to edit
    if product_id:
        product_instance = get_object_or_404(AddProduct, pk=product_id)
    else:
        product_instance = None

    if request.method == 'POST':
        # If the form is submitted
        form = productForm(request.POST, instance=product_instance)
        if form.is_valid():
            # Save the product details
            product = form.save()

            # Handle product images
            new_images = request.FILES.getlist('productImage')
            old_images = product.images.all()

            # Delete old images not included in the new set
            for old_image in old_images:
                if old_image.image not in new_images:
                    old_image.delete()

            # Add new images to the product
            for uploaded_file in new_images:
                productImage.objects.create(product=product, image=uploaded_file)

            messages.success(request, "Product details updated successfully.")
            return redirect('product_detail', product_id=product.id)  # Redirect to product detail page after saving
    else:
        # If it's a GET request or if there's an error in the form submission
        form = productForm(instance=product_instance)

    # Render the template with the form
    return render(request, 'Inventory/editproduct.html', {'form': form})