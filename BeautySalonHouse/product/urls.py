from django.urls import path
from . import views
   # for add product
urlpatterns = [path('productpage', views.product_add_market, name='productpage'),
    path('addproduct', views.AddProduct, name='addproduct'),
    
    path('productdetail/<int:product_id>/', views.productdetail, name='productdetail'),
path('productlist', views.productlist, name='productlist'),
path('addtocart/<int:product_id>', views.addtoCart, name='addtocart'),  
path('cart', views.cart_view, name='cartview'),
path('update_cart/', views.update_cart, name='update_cart'),
path('checkout', views.checkout, name='checkout'),]