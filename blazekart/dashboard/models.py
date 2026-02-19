from django.db import models
from accounts.models import Account
from orders.models import Order
# Create your models here.
class UserProfile(models.Model):
    gender_choice=(
        ('male','Male'),
        ('female','Female'),
        ('other','Other'),
        ('prefer_not_to_say','Prefer not to say'),
    )
    user=models.OneToOneField(Account,on_delete=models.CASCADE,related_name='profile')
    profile_pic=models.ImageField(upload_to='profiles/',blank=True,null=True)
    bio=models.TextField(blank=True)
    date_of_birth=models.DateField(null=True,blank=True)
    gender=models.CharField(max_length=20,choices=gender_choice,blank=True)
    password_updated_at=models.DateTimeField(null=True,blank=True)
    two_factor_enabled=models.BooleanField(default=False)

    def __str__(self):
        return self.user.email
    


class UserAddress(models.Model):
    user=models.ForeignKey(Account,on_delete=models.CASCADE,related_name='addresses')
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    phone=models.CharField(max_length=15)

    address_line_1=models.CharField(max_length=100)
    address_line_2=models.CharField(max_length=100,blank=True)
    city=models.CharField(max_length=50)
    state=models.CharField(max_length=50)
    country=models.CharField(max_length=50)
    pincode=models.CharField(max_length=10)

    label=models.CharField(max_length=50)
    is_default=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.label} - {self.city}'

class BillingAddress(models.Model):
    order=models.OneToOneField(Order,on_delete=models.CASCADE,related_name='billing_address')
    
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    email=models.EmailField()
    phone=models.CharField(max_length=15)

    address_line_1=models.CharField(max_length=100)
    address_line_2=models.CharField(max_length=100,blank=True)
    city=models.CharField(max_length=50)
    state=models.CharField(max_length=50)
    country=models.CharField(max_length=50)
    pincode=models.CharField(max_length=10)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Billing address for {self.order.order_number}"
