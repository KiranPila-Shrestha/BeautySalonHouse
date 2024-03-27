from django.db import models
from django.shortcuts import redirect
from django.contrib.auth.models import User, Group
# Create your models here.


#Category Available:
productCategoryChoice = (
    ('Haircare', 'Haircare'),
    ('Skincare', 'Skincare'),
    ('Nail Care', 'Nail Care'),
    ('Makeup', 'Makeup'),
    ('Fragrances', 'Fragrances'),
    ('Tools and Accessories', 'Tools and Accessories')
)


class addProduct(models.Model):
    productName = models.CharField(max_length=100)
    productCategory = models.CharField(max_length=100, choices=productCategoryChoice)
    productBrand = models.CharField(max_length=100)
    productDescription = models.TextField()
    
    productPrice = models.DecimalField(max_digits=10,decimal_places=2)
    productStock = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.productName
    
    
class productImage(models.Model):
    addProduct = models.ForeignKey(addProduct, related_name = 'images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='inventory/productImage')
    
class cart(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    products = models.ManyToManyField('addProduct')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Cart for {self.user.username}"
    
    def update_total_amount(self):
        #calculate total amount based on the qunatity of each item in the cart
        total = sum(item.product.productPrice * item.Quantity for item in self.cartitem_set.all())
        self.total_amount = total
        self.save()
    
        
    
            
class Cartitem(models.Model):
    cart = models.ForeignKey(cart, on_delete = models.CASCADE)
    product = models.ForeignKey('addProduct', on_delete = models.CASCADE)
    Quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.Quantity} x {self.product.productName} in Cart for {self.cart.user.username}"
    