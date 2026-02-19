from django.contrib import admin
from .models import Order,OrderItem,Payment
# Register your models here.

class OrderAdmin(admin.ModelAdmin):
    list_display=['order_number','user','first_name','last_name','phone','order_total']

class OrderItemAdmin(admin.ModelAdmin):
    list_display=['order','user','product','quantity','product_price','created_at','updated_at']
class PaymentAdmin(admin.ModelAdmin):
    list_display=['payment_id','user','payment_method','amount_paid','status']
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderItem,OrderItemAdmin)
admin.site.register(Payment,PaymentAdmin)