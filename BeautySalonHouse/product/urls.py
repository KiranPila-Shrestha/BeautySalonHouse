from django.urls import path
from . import views
   # for add product
urlpatterns = [path('productpage', views.product_add_market, name='productpage'),
    path('addproduct', views.AddProduct, name='addproduct'),
    path('productdetail', views.productdetail, name='productdetail'),
path('productlist', views.productlist, name='productlist'),
path('addtocart', views.addtoCart, name='addtocart'),
path('checkout', views.checkout, name='checkout'),]