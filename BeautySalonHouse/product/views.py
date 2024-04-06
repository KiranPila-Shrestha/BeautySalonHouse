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


#def addtoCart(request):
 #   return render(request, 'Inventory/addToCart.html')
 
# def place_order(request):
#     if request.method == 'POST':
#         # Retrieve cart details
#         user_cart = cart.objects.get(user=request.user)
#         cart_items = user_cart.cartitem_set.all()
        
#         # Construct the product details and prices strings
#         products_details = "\n".join([f"{item.product.productName} - Quantity: {item.Quantity}" for item in cart_items])
#         prices = "\n".join([f"{item.product.productName}: {item.product.productPrice}" for item in cart_items])
        
#         # Calculate total amount
#         total_amount = sum(item.product.productPrice * item.Quantity for item in cart_items)
        
#         # Create order history record
#         orderHistory.objects.create(
#             user=request.user,
#             products=products_details,
#             prices=prices,
#             total_amount=total_amount
#         )
        
#         # Clear the cart
#         user_cart.cartitem_set.all().delete()
        
#         messages.success(request, "Your order has been placed successfully!")
#         return redirect('home')  # Redirect to home page or any other page
        
#     # Handle cases where the request method is not POST
#     return redirect('cartview')  # Redirect back to the cart view if the request method is not POST


# @login_required
# def order_history(request):
#     orders = OrderHistory.objects.filter(user=request.user).order_by('-date_ordered')
#     return render(request, 'order_history.html', {'orders': orders})

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
     
     
# CHANGE for khalti
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
            pass
            # return redirect('error')
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