from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse ,JsonResponse
from category.models import Category
from .models import Product,Variation,Review,ReviewMedia
from django.db.models import Q
from django.core.paginator import Paginator,EmptyPage
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST,require_http_methods
from django.template.loader import render_to_string
from django.db.models import Count

# Create your views here.
def store(request,slug=None):
    products=Product.objects.filter(is_available=True)
    
    selected_categories=request.GET.getlist('category')
    selected_sizes=request.GET.getlist('size')
    min_price=request.GET.get('min_price')
    max_price=request.GET.get('max_price')

    if selected_categories:
        products=products.filter(category__slug__in=selected_categories)

    if selected_sizes:
        products=products.filter(variation__variation_category='size',variation__variation_value__in=selected_sizes,variation__is_active=True).distinct()

    if min_price:
        products=products.filter(price__gte=min_price)
    if max_price:
        products=products.filter(price__lte=max_price)

    # Sizes for UI
    clothing_sizes = ['small', 'medium', 'large', 'extra large']
    shoe_sizes = ['7', '8', '9', '10', '11']

    paginator=Paginator(products,6)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)

    total_count=page_obj.paginator.count

    if total_count == 0:
        prod_count = "No items found"
    elif total_count == 1:
        prod_count = "1 item found"
    else:
        prod_count = f"{total_count} items found"

    context={
        'fetched_products':page_obj,
        'prod_count': prod_count,
        'selected_categories':selected_categories,
        'selected_sizes':selected_sizes,
        'clothing_sizes': clothing_sizes,
        'shoe_sizes' :shoe_sizes,
        'min_price':min_price,
        'max_price' : max_price,
    }

    return render(request,'store.html',context)

def product_details(request,slug=None,prod_slug=None):
    single_product=Product.objects.get(category__slug=slug,prod_slug=prod_slug)
    print(f'yeh aya ek saman:{single_product.id}')
    colors=Variation.objects.filter(product=single_product,variation_category__iexact = "color" ,is_active=True)
    sizes=Variation.objects.filter(product=single_product,variation_category__iexact = "size" ,is_active=True)
    print("COLORS:", colors)
    print("SIZES:", sizes)

    reviews = (
    Review.objects
    .filter(product=single_product)
    .select_related('user', 'user__profile')
    .prefetch_related('media', 'likes', 'dislikes')
    .annotate(likes_count=Count('likes', distinct=True))
    .order_by('-likes_count', '-created_at')
)

    user_review=None
    if request.user.is_authenticated:
        user_review=Review.objects.filter(user=request.user,product=single_product).first()

    context={
        'single_product':single_product,
        'colors':colors,
        'sizes':sizes,
        'reviews':reviews,
        'user_review' : user_review,
    }
    return render(request,'product_details.html',context)


def search(request):
    if 'search' in request.GET:
        keyword=request.GET['search']
        print(f'keyword joh search kiye:{keyword}')
        if keyword:
            products=Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword)|Q(product_name__icontains=keyword))
            prod_count=products.count()
            print(f'saman aya :{products}')

            if prod_count==0:
                prod_count=(f'Unfortunately, {prod_count} item found related: {keyword}')
            elif prod_count>1:
                prod_count=(f'{prod_count} items found')
            else:
                prod_count=(f'{prod_count} item found')


        else:
            products=Product.objects.all()
            prod_count=products.count()
            if prod_count>1:
                prod_count=(f'{prod_count} items found')
            else:
                prod_count=(f'{prod_count} item found')

        context={
            'fetched_products':products,
            'prod_count':prod_count,
        }


    return render(request,'store.html',context)

@login_required
def add_review(request, product_id):
    if request.method != "POST":
        return redirect('store')

    product = get_object_or_404(Product, id=product_id)

    rating = request.POST.get('rating')
    review_text = request.POST.get('review_text')
    files= request.FILES.getlist('review_media')

    if not rating or not review_text:
        messages.error(request, "Rating and review are required.")
        return redirect(product.get_url())

    if len(review_text) > 1000:
        messages.error(request, "Review cannot exceed 1000 characters.")
        return redirect(product.get_url())
    
    if len(files)>5:
        messages.error(request, "You can upload up to 5 files only.")
        return redirect(product.get_url())


    review, created = Review.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={
            'rating': rating,
            'review_text': review_text
        }
    )
    print(request.FILES)
    if not created:
        review.rating = rating
        review.review_text = review_text
        review.save()
    for f in files:
            media_type = 'video' if f.content_type.startswith('video') else 'image'
            ReviewMedia.objects.create(
                review=review,
                file=f,
                media_type=media_type
            )
    messages.success(request, "Your review has been updated." if not created else "Review submitted successfully!")

    return redirect(product.get_url())



@login_required
def delete_review(request,product_id):
    review=get_object_or_404(Review,id=product_id)

    if review.user != request.user:
        messages.error(request, "You are not allowed to delete this review.")
        return redirect(review.product.get_url())
    
    if request.method != "POST":
        return redirect(review.product.get_url())
    
    review.delete()
    messages.info(request, "Your review has been deleted.")
    return redirect(review.product.get_url())


@login_required
@require_POST
def review_react(request):
    review_id=request.POST.get('review_id')
    action=request.POST.get('action')

    if not review_id or action not in ['like','dislike']:
        return JsonResponse({'error':'Invalid data'},status=400)
    
    review=get_object_or_404(Review,id=review_id)
    user=request.user

    if action == 'like':
        if user in review.likes.all():
            review.likes.remove(user)
        else:
            review.likes.add(user)
            review.dislikes.remove(user)
    
    elif action == 'dislike':
        if user in review.dislikes.all():
            review.dislikes.remove(user)
        else:
            review.dislikes.add(user)
            review.likes.remove(user)
    
    return JsonResponse({
        'likes': review.likes.count(),
        'dislikes': review.dislikes.count(),
        'user_liked': user in review.likes.all(),
        'user_disliked': user in review.dislikes.all(),
    })



@require_http_methods(["GET"])
def load_more_reviews(request):
    product_id = request.GET.get('product_id')  # Changed to GET
    page = int(request.GET.get('page', 1))

    if not product_id:
        return JsonResponse({'error': 'Product ID required'}, status=400)

    reviews = Review.objects.filter(
        product_id=product_id
    ).select_related(
        'user', 'user__profile'
    ).prefetch_related(
        'media', 'likes', 'dislikes'
    ).annotate(
        likes_count=Count('likes',distinct=True)
    ).order_by('-likes_count','-created_at')

    paginator = Paginator(reviews, 6)  # 6 reviews per page

    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        return JsonResponse({'html': '', 'has_next': False})

    html = render_to_string('partials/review_card.html', {
        'reviews': page_obj,
        'user': request.user
    })

    return JsonResponse({
        'html': html,
        'has_next': page_obj.has_next()
    })