from django.db import models
from accounts.models import  Account
from category.models import Category
from django.urls import reverse
from django.db.models import Avg

# Create your models here.
class Product(models.Model):
    product_name=models.CharField(max_length=100,unique=True)
    prod_slug=models.SlugField(max_length=100,unique=True)
    description=models.TextField(max_length=500,blank=True)
    price=models.FloatField()
    images=models.ImageField(upload_to='photos/products')
    stock=models.IntegerField()
    is_available=models.BooleanField(default=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    created_date=models.DateTimeField(auto_now_add=True)
    modified_date=models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.product_name
    
    def get_url(self):
        return reverse('product_details', args=[self.category.slug, self.prod_slug])
    
    def average_rating(self):
        return round(self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0,1)
    
    

variation_category_choice=(
    ('color','color'),
    ('size','size')
)
class Variation(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_category=models.CharField(max_length=100,choices=variation_category_choice)
    variation_value=models.CharField(max_length=100)
    is_active=models.BooleanField(default=True)
    created_date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product.product_name} - {self.variation_value}'
    


    
class Review(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE,related_name='reviews') 
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='reviews')
    review_text=models.TextField(max_length=1000)
    rating=models.PositiveSmallIntegerField()
    
    likes=models.ManyToManyField(Account,related_name='liked_reviews',blank=True)
    dislikes=models.ManyToManyField(Account,related_name='disliked_reviews',blank=True)

    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        unique_together=('user','product')
        ordering=['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.product}"
    
    def total_likes(self):
        return self.likes.count()
    
    def total_dislikes(self):
        return self.dislikes.count()
    
class ReviewMedia(models.Model):
    review=models.ForeignKey(Review,on_delete=models.CASCADE,related_name='media')
    file=models.FileField(upload_to='reviews/media/')
    media_type=models.CharField(max_length=10,choices=(('image','Image'),('video','Video'),))

    def __str__(self):
        return f"Media for Review {self.review.id}"
