from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from . models import *
from .forms import *
from django.contrib import messages
from django.db.models import Sum, F, Q
import json
import requests
from django.http import HttpResponse
from django.db import transaction
from users.models import *
import sweetify 
from django.db.models import Count
from django.core.mail import send_mail
from django.conf import settings
import re
from django.http import Http404 
from django.core.exceptions import ObjectDoesNotExist

 
def is_customer(user):
    if not user.is_superuser and user.is_authenticated:
        if user.userdetail.hasUserBlocked == True and user.userdetail.user_type == 'customer':
            return False
        elif user.userdetail.user_type == 'customer' and user.userdetail.hasUserBlocked == False:
            return True
            # Check if the user is a customer.
        
def is_staff(user):
    if not user.is_superuser and user.is_authenticated:
        if user.userdetail.hasUserBlocked == True and user.groups.filter(name__in=["Hair Technician", "Laser Skin", "Nail Technician", "Makeup Artist"]).exists():
            return False
        elif user.groups.filter(name__in=["Hair Technician", "Laser Skin", "Nail Technician", "Makeup Artist"]).exists() and user.userdetail.hasUserBlocked == False:
            return True

def is_customer_or_is_staff_block(user):
    if user.userdetail.hasUserBlocked == True:
        return user.is_authenticated and user.userdetail.hasUserBlocked == False and (user.groups.filter(name__in=["Hair Technician", "Laser Skin", "Nail Technician", "Makeup Artist"]).exists() or \
            user.userdetail.user_type == 'customer').exists()
    elif user.is_authenticated and user.userdetail.hasUserBlocked == False and (user.groups.filter(name__in=["Hair Technician", "Laser Skin", "Nail Technician", "Makeup Artist"]).exists() or \
            user.userdetail.user_type == 'customer'):
        return user.is_authenticated and user.userdetail.hasUserBlocked == False and (user.groups.filter(name__in=["Hair Technician", "Laser Skin", "Nail Technician", "Makeup Artist"]).exists() or \
            user.userdetail.user_type == 'customer')
     
 #for payment history 
def is_customer_or_superuser(user):
    if user.is_superuser:
        return True
    elif user.userdetail.hasUserBlocked == True and not user.is_superuser:
        return False
        # Check if the user is either a customer or a superuser and is not unauthorized or belongs to specific groups.
        # return user.groups.filter(name__in=["Hair Technician", "Laser Skin", "Nail Technician", "Makeup Artist"]).exists()
    elif user.groups.filter(name__in=["Hair Technician", "Laser Skin", "Nail Technician", "Makeup Artist"]).exists():
        return False
    elif not user.groups.filter(name__in=["Hair Technician", "Laser Skin", "Nail Technician", "Makeup Artist"]).exists():
        return True
            
    
    
def is_superuser(user):
    return user.is_superuser

def product_add_market(request):
    productList = addProduct.objects.all()
    
    SearchFor = request.GET.get("searchFor")
    searchForName = request.GET.get("searchForName")
    print("SearchFor", SearchFor)
    print("searchForName", searchForName)
    
    if SearchFor != "Select category" and SearchFor is not None and searchForName == "": #Search by category only
        # if searchForName != ""
        productList = productList.filter(Q(productCategory__icontains=SearchFor))

    elif SearchFor != "Select category" and SearchFor is not None and searchForName != "":
        productList = productList.filter(Q(productName__icontains=searchForName) | Q(productCategory__icontains=SearchFor))
        
    elif (SearchFor == "Select category" or SearchFor is None) and searchForName != "" and searchForName is not None: #search by name only
        productList = productList.filter(Q(productName__icontains=searchForName))
        
        
    else:
        productList =  addProduct.objects.all()
    
    
    context = {
        'productList' : productList,
        # 'CategoryproductList' : CategoryproductList,
         'productCategoryChoice': productCategoryChoice,
        #  'productImage' : productImage,
        'SearchFor' : SearchFor,
        'searchForName' : searchForName,
    }

    return render(request, 'Inventory/product.html', context)



# for adding product admin

@login_required(login_url='login')
@user_passes_test(is_superuser)
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

    # Check if the room is approved by the admin
    if not productdetail:

        if not (request.user.is_superuser or request.user == productdetail.user):
            raise Http404("Product not found")

    productdetail = get_object_or_404(addProduct, pk=product_id)
    
    
    #to get image of product
    productdetailImage = get_object_or_404(addProduct, id=product_id)
    
    product_image = productImage.objects.filter(addProduct=productdetailImage)
    feedbacks = ProductFeedback.objects.filter(addProduct= product_id)
    
    context ={
        'productlist': productlist,
        'productdetail': productdetail,
        'productdetailImage': productdetailImage,
        'product_image':product_image,
        'feedbacks' : feedbacks,
    }
    
    return render(request, 'Inventory/productdetail.html', context)



@login_required
@user_passes_test(is_superuser)
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

@user_passes_test(is_customer)
@user_passes_test(is_customer_or_is_staff_block)
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
    new_address = request.user.userdetail.address
    new_number = request.user.userdetail.contact_number 

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
   
    user_cart.new_address = new_address
    user_cart.new_number = new_number
    user_cart.save()
    
    sweetify.success(request, "Product has been added to the cart successfully.")
    return redirect ('productpage')

@login_required    
@user_passes_test(is_customer)
@user_passes_test(is_customer_or_is_staff_block)
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

@login_required
@user_passes_test(is_customer)    
@user_passes_test(is_customer_or_is_staff_block) 
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

@login_required
@user_passes_test(is_customer) 
@user_passes_test(is_customer_or_is_staff_block)   
def checkoutpage(request):
    if request.method == "POST":
        user_cart, created = cart.objects.get_or_create(user=request.user)

        if "saveDetails" in request.POST:
            new_address = request.POST.get('address')
            new_number = request.POST.get('phone_number')
          # Validate new phone number
            if not re.match(r'^(98|97)\d{8}$', new_number):
                sweetify.error(request, "New phone number invalid !!")
            else:
                user_cart.new_address = new_address
                user_cart.new_number = new_number
                user_cart.save()
                sweetify.success(request, "New details saved successfully.")
            
        
            user_cart.save()
    cartItems = cart.objects.filter(user=request.user)
    user_detail = UserDetail.objects.get(user=request.user)  # or UserDetail.objects.get(user_id=user_id)
    reward_points = user_detail.reward_points
    context= {
        'cartItems' : cartItems,
        'reward_points':reward_points,
    }
    return render(request, 'Inventory/checkout.html', context)

@login_required
@user_passes_test(is_customer) 
@user_passes_test(is_customer_or_is_staff_block)
def checkout(request):        
    return render(request, 'Inventory/checkout.html')


# #paymenttt
@login_required
@user_passes_test(is_customer)
@user_passes_test(is_customer_or_is_staff_block)
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
        'Authorization': 'key 533fd0199bc04312a0ea3b2dc5edf61b', 
        
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
@login_required
@user_passes_test(is_customer)
@user_passes_test(is_customer_or_is_staff_block)
def verifyKhalti(request):
    url = "https://a.khalti.com/api/v2/epayment/lookup/"
    if request.method == 'GET':
        headers = {
             'accept': 'application/json',
            'Authorization': 'key 533fd0199bc04312a0ea3b2dc5edf61b', 
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
            try:
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
                        
                        # Decreasing the product stock
                        product.productStock -= quantity
                        product.save()
                        
                        # If product is 0 which means: all products are sold out remove the product.
                        if product.productStock == 0:
                            product.isAvailable = False
                            product.save()
                            
                        
                        orderHistoryDetaillInstance =  orderhistoryDetails.objects.create(
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
            except Exception as e:
                print("Error in transaction:", str(e))
              
                transaction.rollback()
                return redirect('error')
                  
        else:
            return redirect('error')
    else:
        pass
        # return redirect('error')
            
    return render(request, 'payment/paymentsuccess.html')



@login_required
@user_passes_test(is_customer)
@user_passes_test(is_customer_or_is_staff_block)
def paymentSuccess(request):
    return render(request, 'payment/paymentsuccess.html')


@login_required
@user_passes_test(is_customer)



@login_required
def delivery_on_cash(request):
    if request.method == 'POST':
        
        # useRewards = int(request.POST.get("hasUsedReward"))
        
        useRewards = request.POST.get("hasUsedReward")
        print("useRewards", useRewards)
        
        if useRewards != "":
            print("here-", useRewards,"-")
            useReward = int(request.POST.get("hasUsedReward"))
            
        else:
            useReward = 0
            
            
         
        print("sure tyoe", type(useReward))
        print("useRewarduseRewarduseRewarduseRewarduseRewarduseRewarduseRewarduseReward", useReward)
        Buyeruser = request.user
        cartInstance = get_object_or_404(cart, user=Buyeruser)
        checkout_total_amount=cartInstance.total_amount,
        print("cartcartcartcartcartcartcartcartcartcartcartcartcartcartcartcart: ", cartInstance)
        cart_itemsInstance = Cartitem.objects.filter(cart = cartInstance)

        with transaction.atomic():
            order = orderplaced.objects.create(
                Buyeruser = Buyeruser,
                total_amount = cartInstance.total_amount,
                order_contact_number = cartInstance.new_number,
                order_address =cartInstance.new_address,
                status = 'Pending',
                paymentType = "cash on delivery"
            )
           
         
            order.rewardpoint = useReward
            order.Buyeruser.userdetail.reward_points += 1
            order.save()
            
            userDetails = order.Buyeruser
            
            rewardPoint = int(Buyeruser.userdetail.reward_points)
            cartTotalAmount = int(cartInstance.total_amount)
            1000 == 1000  
            if checkout_total_amount == cartTotalAmount: # update the rewaed if not used
                print("same amount")
                user_detail = UserDetail.objects.get(user = Buyeruser)  
                user_detail.reward_points += 1
                # reward_point_used = 0
                user_detail.save()
            else:
                print("Different amount")
                user_detail = UserDetail.objects.get(user = Buyeruser)  
                user_detail.reward_points = rewardPoint

                user_detail.save() 
                
                
                orderplaceInstance = orderplaced.objects.filter(Buyeruser=userDetails).exclude(id=order.id)
                
                for orders in orderplaceInstance:
                    orders.rewardpoint = 0
                    orders.save()
                
                # orderplaceInstance.

                # reward_point_used = rewardPoint
            
            for cart_item in cart_itemsInstance:
                product = cart_item.product
                quantity = cart_item.Quantity
                total_amount_product = product.productPrice * quantity
                
                # Decreasing the product stock
                product.productStock -= quantity
                product.save()
                
                # If product is 0 which means: all products are sold out remove the product.
                if product.productStock == 0:
                    product.isAvailable = False
                    product.save()
                    
                
                orderHistoryDetaillInstance =  orderhistoryDetails.objects.create(
                    order_for = order,
                    product = product,
                    quantity = quantity,
                    total_amount_product =total_amount_product
                )

            
                
            cart_itemsInstance.delete()
            cartInstance.delete()
            return render(request, 'payment/paymentsuccess.html')
    else:
        # Redirect to error page if method is not POST
        return redirect('error')



@login_required
@user_passes_test(is_customer_or_superuser) 
def paymentHistory(request):
    orderDetails = []
    allOrderDetails = []
    
    
    orderPaymentHistory = orderplaced.objects.filter(Buyeruser=request.user)
    orderStatusesBuyUser = orderPaymentHistory.values_list('status', flat=True).distinct()
    allOrderPaymentHistory = orderplaced.objects.all()
    for order in allOrderPaymentHistory:
        orderDetail = orderhistoryDetails.objects.filter(order_for=order)
        allOrderDetails.append(orderDetail)
    
    for order in orderPaymentHistory:
        orderDetail = orderhistoryDetails.objects.filter(order_for=order)
        orderDetails.append(orderDetail)
        
    if request.method == 'POST':
        if "confirmOrder" in request.POST: #confirm order
            with transaction.atomic():
                orderID = request.POST.get("orderID")
                print("orderIDorderIDorderIDorderID", orderID)
                orderHistory = orderplaced.objects.get(pk=orderID)
                orderHistory.status = "Completed"
                orderHistory.save()
                
                # orderHistory.Buyeruser.userdetail.reward_points -= orderHistory.rewardpoint
                # orderHistory.save()
                
                user = orderHistory.Buyeruser
                userDetailForReward = UserDetail.objects.get(user = user)
                
                
                if orderHistory.paymentType == "cash on delivery":
                    if orderHistory.rewardpoint != 0:
                        userDetailForReward.reward_points -= orderHistory.rewardpoint
                        userDetailForReward.save()
                        
            
                
                # Get order details
                order_details = ""
                for orderDetail in orderHistory.orderhistorydetails_set.all():
                    order_details += f"Product: {orderDetail.product.productName}\n"
                    order_details += f"Quantity: {orderDetail.quantity}\n"
                    order_details += f"Amount: {orderDetail.total_amount_product}\n"
                
                # Get total amount, reward points used, and payment date
                total_amount = orderHistory.total_amount
                reward_points_used = orderHistory.rewardpoint
                payment_date = orderHistory.date_ordered
                
                # Construct the message
                message = f"""
                    Your order has been completed successfully.

                    Details:
                    {order_details}
                    Total Amount: {total_amount}
                    Reward Points Used: {reward_points_used}
                    Payment Date: {payment_date}
                    
                    Thank you for choosing us!
                    Contact: +01-555778899
                    Aura Salon, Baneshwor
                """
                
                # Send email
                send_mail(
                    "Your Order has been Completed.",
                    message,
                    settings.EMAIL_HOST_USER,
                    [orderHistory.Buyeruser.email],
                    fail_silently=False,
                )
                
                # Success message
                sweetify.success(request, "Order updated successfully!!")
                return redirect('paymentHistory')
                    
        elif "cancelOrder" in request.POST: #reject order
            with transaction.atomic():
                orderID = request.POST.get("orderID")
                orderHistory = orderplaced.objects.get(pk=orderID)
                orderHistory.status = "Rejected"
                orderHistory.save()
                
                
                user = orderHistory.Buyeruser
                print(user)
                
                userDetailForReward = UserDetail.objects.get(user = user)
                print(userDetailForReward)
                
                
                
                userDetailForReward.reward_points = orderHistory.rewardpoint
                userDetailForReward.save()
                
                
                for ordered_product in orderHistory.orderhistorydetails_set.all():
                    product = ordered_product.product
                    quantity = ordered_product.quantity
                    product.productStock += quantity
                    product.save()

                
                
                order_details = ""
                for orderDetail in orderHistory.orderhistorydetails_set.all():
                    order_details += f"Product: {orderDetail.product.productName}\n"
                    order_details += f"Quantity: {orderDetail.quantity}\n"
                    order_details += f"Amount: {orderDetail.total_amount_product}\n"
                    
                    orderDetail.product.productStock -= orderDetail.quantity
                    orderDetail.save()
                
                # Get total amount, reward points used, and payment date
                total_amount = orderHistory.total_amount
                reward_points_used = orderHistory.rewardpoint
                payment_date = orderHistory.date_ordered
                
                # Construct the message
                message = f"""
                    Your order has been Rejected.

                    Details:
                    We regret to inform you that your order has been cancelled.
                    {order_details}
                    Total Amount: {total_amount}
                    Reward Points Used: {reward_points_used}
                    Payment Date: {payment_date}
                    
                    Please feel free to contact us for further assistance.
                    Contact: +01-555778899
                    Aura Salon, Baneshwor
                """
                
                # Send email
                send_mail(
                    "Your Order has been Rejected.",
                    message,
                    settings.EMAIL_HOST_USER,
                    [orderHistory.Buyeruser.email],
                    fail_silently=False,
                )
                print('aaaaa')
                # Success message
                sweetify.success(request, "Order Rejected successfully!!")
                return redirect('paymentHistory')
            
        
        
        elif 'leaveFeedback' in request.POST:
            with transaction.atomic():
                feedback = request.POST.get("feedback")
                rating = request.POST.get("hs-ratings-readonly")
                productID = request.POST.get("productID")
                
                Product = addProduct.objects.get(id=productID)
                current_user = request.user
                
                print("ProductProductProduct", Product)
                print("feedback", feedback)
                print("rating", rating)
                print("productIDproductIDproductIDproductIDproductIDproductID", productID)
                
                if feedback == "" and rating == None:
                    sweetify.error(request, "Empty Feedback!!")

                elif feedback != "" and rating == None:
                    Product.productfeedback_set.create(user=current_user,feedback=feedback)
                    sweetify.success(request, "Thank you for your feedback!")
                elif feedback == "" and rating != None:
                    Product.productfeedback_set.create(user=current_user,rating=rating)
                    sweetify.success(request, "Thank you for your feedback!")
                elif feedback != "" and rating != None:
                    Product.productfeedback_set.create(user=current_user,rating=rating, feedback= feedback)
                    sweetify.success(request, "Thank you for your feedback!")
    #for filterdropdown in dashboard             
    orderStatusCounts = orderplaced.objects.values('status').annotate(count=Count('status'))
    
       
    context = {
        'orderPaymentHistory' : orderPaymentHistory,
        'orderDetails' : orderDetails,
        'allOrderDetails' : allOrderDetails,
        'allOrderPaymentHistory' : allOrderPaymentHistory,
        'orderStatusCounts': orderStatusCounts,
        'orderStatusesBuyUser': orderStatusesBuyUser,
    }

    return render(request, 'payment/paymentHistory.html', context)

#for admin edit product
@login_required
@user_passes_test(is_superuser)
def edit_product(request, product_id):
    # If product_id is provided, fetch the instance of the product to edit
    product_instance = get_object_or_404(addProduct, pk=product_id)
    
    if request.method == 'POST':
        # If the form is submitted
        form = editproductForm(request.POST, instance=product_instance)
        
        print('form', form)
        if form.is_valid():
            # Save the product details
            product = form.save()
            
            # Handle product images
            new_images = request.FILES.getlist('productImage')
            old_images = product.images.all()
            print('new image',new_images)
            # Delete old images not included in the new set
            for old_image in old_images:
                if old_image.image not in new_images:
                    old_image.delete()

            # Add new images to the product
            for uploaded_file in new_images:
                productImage.objects.create(addProduct=product_instance, image=uploaded_file)

            sweetify.success(request, "Product details updated successfully.")
            return redirect('productdetail', product_id=product.id)  # Redirect to product detail page after saving
    else:
        # If it's a GET request or if there's an error in the form submission
        form = productForm(instance=product_instance)
        
    context = {
        'form': form,
        'product_instance': product_instance
    }

    # Render the template with the form
    return render(request, 'Inventory/editproduct.html', context)

