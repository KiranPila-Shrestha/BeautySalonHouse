from django.urls import path
from . import views
   # for add product
urlpatterns = [path('productpage', views.product_add_market, name='productpage'),
    path('addproduct', views.AddProduct, name='addproduct'),
    path('productlist', views.productlist, name='productlist'),
    path('productdetail/<int:product_id>/', views.productdetail, name='productdetail'),
    path('addtocart/<int:product_id>', views.addtoCart, name='addtocart'),  
    path('cart', views.cart_view, name='cartview'),
    path('update_cart/', views.update_cart, name='update_cart'),
    path('checkout_test', views.checkout, name='checkout'),
    path('placeorder', views.checkoutpage, name='checkoutpage'),
   
    #for payment
    path('paymentSucessful', views.verifyKhalti, name='paymentSucessful'),
    path('initiate', views.initkhalti, name='initiate'),
    #for payment history
    path('paymentHistory', views.paymentHistory, name='paymentHistory'),
    # urls.py
    path('product/<int:product_id>/', views.edit_product, name='edit_product'),

    path('error', views.verifyKhalti, name='error'),
     path('CashonDelivery', views.delivery_on_cash, name='CashonDelivery'),
  

]
