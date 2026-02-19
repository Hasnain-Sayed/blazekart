from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product,Variation
from .models import Cart,CartItem,WishList
from django.contrib import messages
from .utils import adjust_to_stock

# Create your views here.
def handle_product_action(request, product_id):
    action = request.POST.get("action")
    if action == "cart":
        return add_cart(request, product_id)
    elif action == "wishlist":
        return add_to_wishlist(request, product_id)
    else:
        messages.error(request, "Invalid action")
        return redirect('product_details', slug=Product.objects.get(id=product_id).category.slug,
                        prod_slug=Product.objects.get(id=product_id).prod_slug)


def _cart_id(request):#  yeh ek privaye function hai and yeh directly pass hota h
    cart_id=request.session.session_key
    print(f'yeh hai 1st:{cart_id}')

    if not cart_id:
        request.session.create()
        cart_id=request.session.session_key
        print(f' second : {cart_id}')
    return cart_id

def add_cart(request,product_id):
    prod_fetch=Product.objects.get(id=product_id)
    print(f'product aya :{prod_fetch}')

    if request.user.is_authenticated:
        cart,created=Cart.objects.get_or_create(cart_id=_cart_id(request)) 
        print(f'kya ya hai cart:{cart} and created :{created}')

        if prod_fetch.stock <= 0:
            messages.error(request, "This product is out of stock.")
            return redirect('store')
        product_variation=[]

        if request.method == "POST":
            for key,value in request.POST.items():
                try:
                    variation=Variation.objects.get(product=prod_fetch,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except Variation.DoesNotExist:
                    pass
        

        cart_items=CartItem.objects.filter(product=prod_fetch,user=request.user)
        already_in_cart=None
        
        for item in cart_items:
            existing_variations=list(item.variations.all())
            if existing_variations==product_variation:
                already_in_cart=item
                break
            # print(Variation.objects.all().values()) 

        if already_in_cart:
            adjusted_qty,limited=adjust_to_stock(prod_fetch,already_in_cart.quantity+1)
            already_in_cart.quantity=adjusted_qty
            already_in_cart.save()

            if limited:
                request.session['stock_limit_reached'] = True
        else:
            cart_item=CartItem.objects.create(product=prod_fetch,user=request.user,quantity=1)
            cart_item.variations.set(product_variation)
            cart_item.save()
        

    else:
        # cart_id=_cart_id(request) could be done like this for readibility purpose, 
        cart,created=Cart.objects.get_or_create(cart_id=_cart_id(request)) #this work as it is
        print(f'kya ya hai cart:{cart} and created :{created}')
        if prod_fetch.stock <= 0:
            messages.error(request, "This product is out of stock.")
            return redirect('store')
        product_variation=[]

        if request.method == "POST":
            for key,value in request.POST.items():
                try:
                    variation=Variation.objects.get(product=prod_fetch,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except Variation.DoesNotExist:
                    pass
        

        cart_items=CartItem.objects.filter(product=prod_fetch,cart=cart)
        already_in_cart=None

        for item in cart_items:
            existing_variations=list(item.variations.all())
            if existing_variations==product_variation:
                already_in_cart=item
                break
            # print(Variation.objects.all().values()) 

        if already_in_cart:
            adjusted_qty,limited=adjust_to_stock(prod_fetch,already_in_cart.quantity+1)
            already_in_cart.quantity=adjusted_qty
            already_in_cart.save()

            if limited:
                request.session['stock_limit_reached'] = True
        else:
            cart_item=CartItem.objects.create(product=prod_fetch,cart=cart,quantity=1)
            cart_item.variations.set(product_variation)
            cart_item.save()




    return redirect('cart')


def cart(request):
    
    wishlist_items=[]
    if request.user.is_authenticated:
        cart_items=CartItem.objects.filter(user=request.user,is_active=True)
        wishlist_items=WishList.objects.filter(user=request.user)

    else:
        cart_id,created=Cart.objects.get_or_create(cart_id=_cart_id(request))
        cart_items=CartItem.objects.filter(cart=cart_id,is_active=True)
        
    print(f'cart items:{cart_items}')
    stock_limit_reached = request.session.pop('stock_limit_reached', False)

    total=0
    tax=0
    for item in cart_items:
        subtotals=item.product.price * item.quantity
        total=total+subtotals
    tax=(total*18)/100
    final_total=round((total+tax),2)

    context={
        'cart_items':cart_items,
        'wishlistitems':wishlist_items,
        'total':total,
        'tax':tax,
        'final_total':final_total,
        'stock_limit_reached':stock_limit_reached,
    }


    return render(request,'cart.html',context)


def remove_cart_item(request,product_id,cart_item_id):
    if request.user.is_authenticated:
        cart_item=CartItem.objects.get(product=product_id,id=cart_item_id,user=request.user)
        cart_item.delete()
    else:

        cart_item=CartItem.objects.get(product=product_id,id=cart_item_id)
        cart_item.delete()
    return redirect('cart')


def reduce_cart_item(request,product_id,cart_item_id):
        
    if request.user.is_authenticated:
        cart_item=CartItem.objects.get(product=product_id,id=cart_item_id,user=request.user)
        if cart_item.quantity>1:
            cart_item.quantity-=1
            cart_item.save()
        else:
            cart_item.delete()
    else:  
        cart_item=CartItem.objects.get(product=product_id,id=cart_item_id)
        if cart_item.quantity>1:
            cart_item.quantity-=1
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('cart')



def update_cart(request,product_id,cart_item_id):

    if request.user.is_authenticated:
        cart_item=CartItem.objects.get(id=cart_item_id, product_id=product_id,user=request.user)
        if request.method == "POST" :
            quantity = request.POST.get("input_box")
            
            if quantity is None or quantity.strip() == "":
                quantity=cart_item.quantity
            else:
                quantity=int(quantity)
                

            if quantity<1:
                quantity=1
            adjusted_qty,limited=adjust_to_stock(cart_item.product,quantity)
            cart_item.quantity=adjusted_qty
            cart_item.save()

            if limited:
                request.session['stock_limit_reached'] = True

    else:
        cart_item=CartItem.objects.get(id=cart_item_id, product_id=product_id)
        if request.method == "POST" :
            quantity = request.POST.get("input_box")
            
            if quantity is None or quantity.strip() == "":
                quantity=cart_item.quantity
            else:
                quantity=int(quantity)
                

            if quantity<1:
                quantity=1
            adjusted_qty,limited=adjust_to_stock(cart_item.product,quantity)
            cart_item.quantity=adjusted_qty
            cart_item.save()
            if limited:
                request.session['stock_limit_reached'] = True
    return redirect('cart')


def add_to_wishlist(request,product_id):
    if not request.user.is_authenticated:
        messages.warning(request,"Please log in to add items to your Wishlist")
        return redirect('login')


    product=Product.objects.get(id=product_id)
    if product.stock <= 0:
            messages.error(request, "This product is out of stock.")
            return redirect('store')
    product_variation=[]
    if request.method == "POST":
        for key,value in request.POST.items():
            print(key,value)
            try:
                variation=Variation.objects.get(product=product,
                                                variation_category__iexact=key,
                                                variation_value__iexact=value)
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass
        print(product_variation)
    wishlist_items=WishList.objects.filter(product=product,user=request.user)
    already_in_wishlist=None
    for item in wishlist_items:
        existing_variation=list(item.variations.all())

        if existing_variation==product_variation:
            already_in_wishlist = item
            break
    
    if already_in_wishlist:
        messages.error(request, "This item with selected variations is already in your Wishlist.")
    else:
        wishlist_item=WishList.objects.create(
            user=request.user,
            product=product,
            quantity=1
            )
        wishlist_item.variations.set(product_variation)
        wishlist_item.save()
  
        messages.success(request,"Item Added To Your Wishlist.")
    return redirect('product_details', slug=product.category.slug,prod_slug= product.prod_slug)

       
def remove_wishlist_item(request,product_id):
    if not request.user.is_authenticated:
        messages.warning(request,"Please log in to customize your Wishlist")
        return redirect('login')
    
    wishlist_item=WishList.objects.filter(product_id=product_id,user=request.user).first()
    print(f'wishlist ka item remove hua:{wishlist_item}')
    wishlist_item.delete()
    
    return redirect('cart')



def move_to_wishlist(request, product_id, item_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to customize your wishlist")
        return redirect('login')

    cart_item = get_object_or_404(CartItem, id=item_id, product_id=product_id, user=request.user)

    # Collect the variations of this cart item
    cart_variations=list(cart_item.variations.all())

    # Check if same product with SAME variations exists in wishlist
    existing_items=WishList.objects.filter(product=cart_item.product,user=request.user)

    for item in existing_items:
        existing_variations=list(item.variations.all())
        if set(cart_variations)==set(existing_variations):
            # SAME item exists → increase quantity
            item.quantity+=cart_item.quantity or 1
            item.save()
            cart_item.delete()
            return redirect('cart')


    wishlist_item = WishList.objects.create(
        product=cart_item.product,
        user=request.user,
        quantity=cart_item.quantity
    )
    # Copy variations
    for var in cart_item.variations.all():
        wishlist_item.variations.add(var)
    wishlist_item.save()

    # Optionally remove from cart
    cart_item.delete()

    return redirect('cart')




def move_to_cart(request, product_id, item_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to customize your cart")
        return redirect('login')

    # Get the wishlist item
    wishlist_item = get_object_or_404(WishList, id=item_id, product_id=product_id, user=request.user)
    product=wishlist_item.product
    wishlist_variations=list(wishlist_item.variations.all())

    # Check if item is already in the cart
    cart_items = CartItem.objects.filter(product_id=product_id, user=request.user)
    matched_cart_item=None

    # Compare variations to find exact match
    for item in cart_items:
        cart_variations=list(item.variations.all())
        if set(wishlist_variations)==set(cart_variations):
            matched_cart_item=item
            break

    if matched_cart_item:
        # Increase quantity if exact variation match found
        adjusted_qty,limited=adjust_to_stock(product,matched_cart_item.quantity+(wishlist_item.quantity or 1))
        matched_cart_item.quantity=adjusted_qty
        matched_cart_item.save()
        if limited:
                request.session['stock_limit_reached'] = True
    else:
        # Create a NEW cart item if variations differ
        new_qty,limited=adjust_to_stock(product,wishlist_item.quantity or 1)
        if limited:
            request.session['stock_limit_reached'] = True 
        new_cart_item=CartItem.objects.create(
            product=product,
            user=request.user,
            quantity=new_qty
        )
        new_cart_item.variations.set(wishlist_variations)
        new_cart_item.save()

    # Remove the item from wishlist
    wishlist_item.delete()
    return redirect('cart')
