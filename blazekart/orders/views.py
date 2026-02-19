from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cart.models import Cart,CartItem
from store.models import Product
from .models import Order,OrderItem,Payment
from dashboard.models import UserAddress,BillingAddress
import random
from datetime import date
import json
from django.http import JsonResponse,HttpResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


# Create your views here.

def checkout(request):

    
    if not request.user.is_authenticated:
        messages.warning(request, "Guest must sign-in before checking out!")
        return redirect("login")
    
    else:
        current_user=request.user
        email=current_user.email
        cart_items=CartItem.objects.filter(user=current_user)
        cart_count=cart_items.count()
        addresses = UserAddress.objects.filter(user=request.user)
        if cart_count<=0:
            return redirect('store')
        total=0
        tax=0
        for item in cart_items:
            subtotals=item.product.price * item.quantity
            total=total+subtotals
        tax=(total*18)/100
        final_total=round((total+tax),2)
        if request.method=="POST":
            user_address=UserAddress.objects.filter(user=request.user,is_default=True).first()

            order=Order.objects.create(
                user=request.user,  #we can use either this to fetch user or current_user
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'],
                email=request.POST['email'],
                phone=request.POST['phone'],
                address_line_1=request.POST['address_line_1'],
                address_line_2=request.POST['address_line_2'],
                city=request.POST['city'],
                state=request.POST['state'],
                country=request.POST['country'],
                pincode=request.POST['pincode'],
                order_note=request.POST['order_note'],
                tax=tax,
                order_total=final_total,
                ip=request.META.get('REMOTE_ADDR'),
            )

            today=date.today().strftime("%Y%m%d")
            random_num=random.randint(1000,9999)

            order.order_number=f"{today}{order.id}{random_num}"
            order.save()
            if user_address:
                BillingAddress.objects.create(
                    order=order,
                    first_name=user_address.first_name,
                    last_name=user_address.last_name,
                    email=order.email,
                    phone=user_address.phone,
                    address_line_1=user_address.address_line_1,
                    address_line_2=user_address.address_line_2,
                    city=user_address.city,
                    state=user_address.state,
                    country=user_address.country,
                    pincode=user_address.pincode,
                )

            order=Order.objects.get(user=current_user,is_ordered=False,order_number=order.order_number)
            context={
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                'final_total':final_total,
            }

            return render(request,'orders/payments.html',context)
            
        context={
            'tax':tax,
            'final_total':final_total,
            'cart_items':cart_items,
            'cart_count':cart_count,
            'total':total,
            'addresses':addresses,
            'email':email,
        }

    return render(request, "orders/checkout.html",context)



def payments(request):
    body=json.loads(request.body)
    print(f'body aya:{body}')

    order=Order.objects.get(user=request.user,is_ordered=False,order_number=body['orderID'])
    payment=Payment(user=request.user,payment_id=body['transID'],payment_method=body['payment_method'],amount_paid=order.order_total,status=body['status'])
    payment.save()

    order.payment=payment
    order.is_ordered=True
    order.save()

    cart_items=CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderitem=OrderItem()
        orderitem.order=order
        orderitem.payment=payment
        orderitem.user=request.user
        orderitem.product=item.product
        orderitem.quantity=item.quantity
        orderitem.product_price=item.product.price
        orderitem.is_ordered=True
        orderitem.save()

        cart_item=CartItem.objects.get(id=item.id)
        product_variation=cart_item.variations.all()
        orderitem=OrderItem.objects.get(id=orderitem.id)
        orderitem.variations.set(product_variation)
        orderitem.save()
        product=Product.objects.get(id=item.product_id)
        product.stock-=item.quantity
        product.save()
    CartItem.objects.filter(user=request.user).delete()


    order_items = OrderItem.objects.filter(order=order)
# Prepare product data for template
    products_data = []
    for item in order_items:
        variations = [f"{v.variation_category}: {v.variation_value}" for v in item.variations.all()]
        products_data.append({
        'name': item.product.product_name,
        'quantity': item.quantity,
        'price': item.product_price,
        'variations': variations
    })

    mail_subject="Thank You For Ordering"
    message=render_to_string('orders/order_receive_email.html',
                             {
                                    'user':request.user,
                                    'order':order,
                                    'products':products_data,
                                    'payment_id':payment.payment_id
                                })
    to_email=request.user.email
    send_mail=EmailMessage(mail_subject,message,to=[to_email])
    send_mail.content_subtype = "html"
    sent=send_mail.send()

    print(f' send hua kya :{sent}')
    data={
        'order_number':order.order_number,
        'transID':payment.payment_id
    }
    return JsonResponse(data)


    # return render(request,'orders/payments.html')

def order_complete(request):
    order_number=request.GET.get('order_number')
    transID=request.GET.get('payment_id')
    print(f'order number aya:{order_number}, trandsid : {transID}')

    try:
        order=Order.objects.get(order_number=order_number,is_ordered=True)
        ordered_items=OrderItem.objects.filter(order=order)
        order_count=0
        payment=Payment.objects.get(payment_id=transID)
        for item in ordered_items:
            subtotal=item.product_price * item.quantity
            order_count+=item.quantity
        context={
            'order':order,
            'ordered_items':ordered_items,
            'payment':payment,
            'subtotal':subtotal,
            'order_count':order_count,
        }


        return render(request,'orders/order_complete.html',context) 
    except Order.DoesNotExist:
        messages.error(request,'Order Not Found')
        return redirect('store')
