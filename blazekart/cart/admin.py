from django.contrib import admin
from .models import Cart,CartItem,WishList
# Register your models here.

class CartAdmin(admin.ModelAdmin):
    list_display=['cart_id','date_added']

class CartItemAdmin(admin.ModelAdmin):
    list_display=['product','cart','user','quantity','is_active']

class WishListAdmin(admin.ModelAdmin):
    list_display=['id','product','user','quantity','added_at']

admin.site.register(Cart,CartAdmin)
admin.site.register(CartItem,CartItemAdmin)
admin.site.register(WishList,WishListAdmin)