from django.shortcuts import render
from django.http import HttpResponse 
from store.models import Product
import random
from django.db.models import Avg

# Create your views here.
def home(request):
    products=Product.objects.filter(stock__gt=0).annotate(avg_rating=Avg('reviews__rating'))
    products=random.sample(list(products),k=4)
    context={
        'all_prods':products,
    }

    return render(request,'index.html',context)