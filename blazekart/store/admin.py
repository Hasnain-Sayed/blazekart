from django.contrib import admin
from .models import Product,Variation,Review,ReviewMedia
from django.utils.html import format_html

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields={'prod_slug':('product_name',)}
    list_display=['product_name','price','stock','is_available','category']
admin.site.register(Product,ProductAdmin)

class VariationAdmin(admin.ModelAdmin):
    list_display=['product','variation_category','variation_value']
admin.site.register(Variation,VariationAdmin)


class ReviewMediaInline(admin.TabularInline):
    model=ReviewMedia
    extra=0
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.media_type == 'image':
            return format_html(
                '<img src="{}" style="width:80px; height:auto;" />',
                obj.file.url
            )
        return "Video"

class ReviewAdmin(admin.ModelAdmin):
    list_display=('id','product','user','rating_stars','likes_count','dislikes_count','created_at',)

    list_filter = ('rating', 'created_at', 'product')
    search_fields = ('user__email', 'product__product_name', 'review_text')
    ordering = ('-created_at',)

    inlines = [ReviewMediaInline]

    readonly_fields = ('user', 'product','created_at', 'updated_at')

    def rating_stars(self, obj):
        return '⭐' * obj.rating

    rating_stars.short_description = 'Rating'

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'

    def dislikes_count(self, obj):
        return obj.dislikes.count()
    dislikes_count.short_description = 'Dislikes'
admin.site.register(Review,ReviewAdmin)

class ReviewMediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'media_type')
    list_filter = ('media_type',)
admin.site.register(ReviewMedia,ReviewMediaAdmin)