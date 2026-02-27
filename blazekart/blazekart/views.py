from django.shortcuts import render
from django.http import HttpResponse 
from store.models import Product
import random
from django.db.models import Avg

# Create your views here.
def home(request):
    products=Product.objects.filter(stock__gt=0).annotate(avg_rating=Avg('reviews__rating'))
    products = list(products)
    sample_size = min(len(products), 4)

    featured_products = random.sample(products, sample_size)
    context={
        'all_prods':featured_products,
    }

    return render(request,'index.html',context)