from django.db import models
from store.models import Product,Variation
from accounts.models import Account

# Create your models here.
class Cart(models.Model):
    cart_id=models.CharField(max_length=300,blank=True,null=True)
    date_added=models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id
    
class CartItem(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,blank=True,null=True)
    user=models.ForeignKey(Account,on_delete=models.CASCADE,null=True,blank=True)
    quantity=models.IntegerField(default=0)
    variations=models.ManyToManyField(Variation,blank=True)
    is_active=models.BooleanField(default=True)

    def subtotal(self):
        return self.product.price * self.quantity
    
class WishList(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=0)
    variations=models.ManyToManyField(Variation,blank=True)
    added_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.product_name

    
