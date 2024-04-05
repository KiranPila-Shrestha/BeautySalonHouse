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
                    print( user_cart.total_amount)
                    
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
                
           

        # Check if reward points are sufficient for a discount
       
            
            user_cart.update_total_amount()
            print("Total amount before saving:", user_cart.total_amount)
            user_cart.save()
            print("Total amount after saving:", user_cart.total_amount)
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
        "website_url": "http://127.0.0.1:8000",
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
    print("headerrrrrrr", headers)
    # try:
    response = requests.request("POST", url, headers=headers, data=payload)
    print("responseresponse:", response)
    new_res = json.loads(response.text)
    print("new_resnew_resnew_res:", new_res)
    

    payment_url = new_res.get('payment_url')
    print("payment_urlpayment_urlpayment_urlpayment_url:", payment_url)
    
    if payment_url:
        return redirect(payment_url)
    else:
        messages.error(request, "Something went wrong.")
        print("No payment found", new_res)
        return HttpResponse("Payment URL not found")
    # except Exception as e:
    #     print("Error occurred during payment initiation:", e)
    #     return HttpResponse("An error occurred during payment")
     
     
     

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
            cart = get_object_or_404(cart, user=Buyeruser)
            print("cartcartcartcartcartcartcartcartcartcartcartcartcartcartcartcart: ", cart)
            cart_items = Cartitem.objects.filter(cart = cart)
            # with transaction.atomic():
            
            #get the cart items before clearing
            # cart.items.clear()
            
            order = orderplaced.objects.create(
                Buyeruser = Buyeruser,
                total_amount = cart.total_amount,
                order_contact_number = cart.new_number,
                order_address =cart.new_address,
                status = 'Pending'
            )
            
            
            user_detail = UserDetail.objects.get(user = Buyeruser)
            user_detail.reward_points += 1
            user_detail.save()
            
            reward_point_used = 0
            if user_detail. reward_points >= 10:
                reward_point_used = user_detail.reward_points
                order.total_amount -= reward_point_used
                user_detail.reward_points += 1
                user_detail.save()
            
            for cart_item in Cartitem:
                product = cart_item.product
                quantity = cart_item.Quantity
                total_amount_product = product.productPrice * quantity
                
                orderhistory.objects.create(
                    order_for = order,
                    product = product,
                    quantity = quantity,
                    total_amount_product =total_amount_product
                )
            order.rewardpoint = reward_point_used
            order.save()
            cart.delete()
            
            
        else:
            pass
            # return redirect('error')
    else:
        pass
            
            
        #     #calculate total amount including if rewards is incluede
            
        #     total_amount = cart.total_amount()
            
        #     #check if reward us used
        #     user_detail = UserDetail.objects.get(User = request.user)
        #     if  user_detail.reward_points >= 10:
        #         reward_point_used = user_detail.reward_points
        #         total_amount -= reward_point_used 
                
        #         user_detail.reward_points += 1
        #         user_detail.save()
                
        #     else:
        #         reward_point_used = 0
                
        #      # Award 1 reward point for each purchase
        #     user_detail.reward_points += 1
        #     user_detail.save()
            
        #     #created an object to store about order
        #     order = orderHistory.objects.create(user = request.user, total_amount = total_amount, product='\n'.join([f"{item.Quantity} x {item.product.productName} ({item.product.productBrand}): ${item.product.productPrice}" for item in cart_items]),quantity=sum([item.Quantity for item in cart_items]),rewardpoint=reward_point_used, status='Pending')

        #     print("SUCCESS PAYMENT")
        #     return redirect('addtocart')
        # else:
        #     print("ERRRRRRRRRRRRRRRRRRRRRROR")
        #     pass
        #     # return redirect('error')
    return render(request, 'payment/paymentsuccess.html')


# cart bata Sub total nikalne 
# if reward xa sub minus 

def paymentSuccess(request):
    return render(request, 'payment/paymentsuccess.html')

