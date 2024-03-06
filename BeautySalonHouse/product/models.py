from django.db import models
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
    productCategory = models.CharField(max_length=100)
    productBrand = models.CharField(max_length=100)
    productDescription = models.TextField()
    
    productPrice = models.DecimalField(max_digits=10,decimal_places=2)
    productStock = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.productName
    
    
class productImage(models.Model):
    addProduct = models.ForeignKey(addProduct, related_name = 'images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/inventory/productImage')
    
    