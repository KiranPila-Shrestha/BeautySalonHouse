from django.contrib import admin
from product.models import *

# Register your models here.
admin.site.register(addProduct)
admin.site.register(productImage)
admin.site.register(cart)
admin.site.register(Cartitem)
admin.site.register(orderplaced)
admin.site.register(orderhistoryDetails)
