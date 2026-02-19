from django.contrib import admin
from .models import UserProfile,UserAddress
# Register your models here.

class UserProfileAdmin(admin.ModelAdmin):
    list_display=['user']
admin.site.register(UserProfile,UserProfileAdmin)

class UserAddressAdmin(admin.ModelAdmin):
    list_display=['user','label','city','state','country','is_default','created_at']
    list_filter=('is_default','city','country')
admin.site.register(UserAddress,UserAddressAdmin)