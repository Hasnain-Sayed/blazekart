from django.db import models
from accounts.models import Account
from store.models import Product,Variation
from datetime import date
# Create your models here.

class Payment(models.Model):
    user=models.ForeignKey(Account,on_delete=models.SET_NULL,null=True)
    payment_id=models.CharField(max_length=100)
    payment_method=models.CharField(max_length=100)
    amount_paid=models.CharField(max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=50)

    def __str__(self):
        return self.payment_id

class Order(models.Model):

    STATUS=(
        ('New','New'),
        ('Accepted','Accepted'),
        ('Shipped','Shipped'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
    )

    user=models.ForeignKey(Account,on_delete=models.SET_NULL,null=True)
    payment=models.ForeignKey(Payment,on_delete=models.SET_NULL,null=True,blank=True)
    order_number=models.CharField(max_length=50,unique=True)
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    phone=models.CharField(max_length=15)
    email=models.EmailField(max_length=100)
    address_line_1=models.CharField(max_length=100)
    address_line_2=models.CharField(max_length=100,blank=True)
    city=models.CharField(max_length=50)
    state=models.CharField(max_length=50)
    country=models.CharField(max_length=50)
    pincode=models.CharField(max_length=10)
    order_note=models.CharField(max_length=150,blank=True)
    order_total=models.FloatField()
    tax=models.FloatField()
    status=models.CharField(max_length=15,choices=STATUS,default="New")
    ip=models.CharField(max_length=40,blank=True)
    is_ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'
    
    def total(self):
        return round((self.order_total - self.tax),2)
    
    def order_date(self):
        return self.created_at.strftime("%d %b %Y")


    def __str__(self):
        return self.order_number
    
class OrderItem(models.Model):
    user=models.ForeignKey(Account,on_delete=models.SET_NULL,null=True)
    payment=models.ForeignKey(Payment,on_delete=models.SET_NULL,null=True,blank=True)
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variations=models.ManyToManyField(Variation,blank=True)
    quantity=models.IntegerField()
    product_price=models.FloatField()
    is_ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def subtotal(self):
        return self.product_price * self.quantity

    def __str__(self):
        return self.product.product_name
    

    



