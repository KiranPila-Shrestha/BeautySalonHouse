from django.db import models
from product.models import addProduct, cart
from django.contrib.auth.models import User, Group
from django.utils import timezone

class order_payment(models.Model):
    product = models.ForeignKey(addProduct,  on_delete=models.CASCADE)
    user_buyer= models.ForeignKey(User, on_delete = models.CASCADE)
    total_quantity =  models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10,decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_time = models.TimeField(default=timezone.now)
    
    
# Create your models here.

