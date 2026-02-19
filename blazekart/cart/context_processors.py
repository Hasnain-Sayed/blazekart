from .models import Cart,CartItem
from .views import _cart_id
def cart_count(request):

    if request.user.is_authenticated:
        try:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True)

            cart_count=0
            for item in cart_items:
                cart_count+=item.quantity
        except Cart.DoesNotExist:
            cart_count=0
    else: 
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart)
            
            cart_count=0
            for item in cart_items:
                cart_count+=item.quantity
        except Cart.DoesNotExist:
            cart_count=0

    return dict(cart_count=cart_count)