from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from cart.models import CartItem,Variation,WishList
from accounts.models import Account
from cart.utils import adjust_to_stock
from orders.models import Order,OrderItem,Payment
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import black
from django.contrib import auth
from django.contrib import messages
from .models import UserProfile,UserAddress,BillingAddress
from django_otp.plugins.otp_totp.models import TOTPDevice

# Create your views here.
def dashboard(request):
    profile=UserProfile.objects.get(user=request.user)
    cartitems=CartItem.objects.filter(user=request.user)
    wishlists=WishList.objects.filter(user=request.user)
    address=UserAddress.objects.filter(user=request.user)
    orders=Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    cartitems_count=cartitems.count()
    wishlist_count=wishlists.count()
    order_count=orders.count()
    address_count=address.count()



    context={
        'profile':profile,
        'cartitems_count' : cartitems_count,
        'wishlist_count' : wishlist_count,
        'order_count' : order_count,
        'address_count' : address_count,
        'orders':orders,
        'address':address,
    }


    return render(request,'dashboard/dashboard.html',context)



def dbcart(request):
    cartitems=CartItem.objects.filter(user=request.user)
    
    total=0
    tax=0
    for item in cartitems:
        subtotals=item.product.price * item.quantity
        total=total+subtotals
    tax=(total*18)/100
    final_total=round((total+tax),2)
    stock_limit_reached = request.session.pop('stock_limit_reached', False)

    context={
        'cartitems':cartitems,
        'total':total,
        'tax':tax,
        'final_total':final_total,
        'stock_limit_reached': stock_limit_reached,
    }
    
    return render(request,'dashboard/dbcart.html',context)



def remove_dbcart(request,product_id,cart_item_id):
    cart_item=CartItem.objects.get(product=product_id,id=cart_item_id,user=request.user)
    cart_item.delete()

    return redirect('dbcart')



def dbwishlist(request):
    wishlist_items=WishList.objects.filter(user=request.user)
    stock_limit_reached = request.session.pop('stock_limit_reached', False)

    context={
        'wishlist_items':wishlist_items,
        'stock_limit_reached': stock_limit_reached,
    }
    return render(request,'dashboard/dbwishlist.html',context)



def remove_dbwishlist(request,product_id):
    wishlistitem=WishList.objects.get(user=request.user,product_id=product_id)
    wishlistitem.delete()
    return redirect('dbwishlist')



def move_to_dbcart(request,product_id,item_id):
    wishlistitem=get_object_or_404(WishList,user=request.user,product_id=product_id,id=item_id)
    product=wishlistitem.product
    wishlist_variations=list(wishlistitem.variations.all())

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
        adjusted_qty,limited=adjust_to_stock(product,matched_cart_item.quantity+(wishlistitem.quantity or 1))
        matched_cart_item.quantity=adjusted_qty
        matched_cart_item.save()
        if limited:
            request.session['stock_limit_reached'] = True
    else:
        # Create a NEW cart item if variations differ
        new_qty,limited=adjust_to_stock(product,wishlistitem.quantity or 1)
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
    wishlistitem.delete()
    return redirect('dbcart')


def recent_orders(request):
    payments=Payment.objects.filter(user=request.user)
    orders=Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    order_count=orders.count()

    order_complete=0
    order_new=0
    order_cancelled=0
    for order in orders:
        if order.status=='Completed':
            print('completed')
            order_complete+=1
        elif order.status=='New':
            print('new')
            order_new+=1
        elif order.status=='Cancelled':
            order_cancelled+=1



    print(f'order count aya kya:{order_count}')

    context={
        'orders':orders,
        'order_count':order_count,
        'order_complete':order_complete,
        'order_new':order_new,
        'order_cancelled': order_cancelled,
    }

    return render(request,'dashboard/recent_orders.html',context)

def order_details(request,order_num):
    orderitems=OrderItem.objects.filter(user=request.user,order__order_number=order_num)
    order=Order.objects.get(user=request.user,order_number=order_num,is_ordered=True)

    payment=order.payment

    billing_address=BillingAddress.objects.filter(order=order).first()

    address=UserAddress.objects.filter(user=request.user,is_default=True).first()

    if not address:
        address=UserAddress.objects.filter(user=request.user).last()
    context={
        'orderitems':orderitems,
        'order':order,
        'payment':payment,
        'address':address,
        'billaddr' : billing_address,
    }
    
    return render(request,'dashboard/order_details.html',context)



def download_invoice(request, order_number):
    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user,
        is_ordered=True
    )

    items = OrderItem.objects.filter(order=order)
    billing = BillingAddress.objects.filter(order=order).first()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice-{order.order_number}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    margin = 50
    y = height - margin

    # ================= MODERN HEADER WITH PURPLE GRADIENT =================
    # Purple header block
    p.setFillColorRGB(0.42, 0.22, 0.58)  # Rich purple color
    p.rect(0, height - 140, width, 140, fill=1, stroke=0)
    
    # Company name (top right)
    p.setFillColorRGB(1, 1, 1)
    p.setFont("Helvetica-Bold", 16)
    p.drawRightString(width - margin, height - 50, "BlazeKart")
    
    # Company details (top right, smaller)
    p.setFont("Helvetica", 9)
    p.drawRightString(width - margin, height - 68, "blazekart.help@gmail.com")
    p.drawRightString(width - margin, height - 82, "+91 9XXXXXXXXX")
    p.drawRightString(width - margin, height - 96, "City, State")
    p.drawRightString(width - margin, height - 110, "Country - Pincode")
    
    # Large "INVOICE" text (left side)
    p.setFont("Helvetica-Bold", 42)
    p.drawString(margin, height - 110, "INVOICE")
    
    y = height - 180
    p.setFillColorRGB(0, 0, 0)

    # ================= INVOICE INFO BOX =================
    info_box_y = y
    p.setFont("Helvetica-Bold", 9)
    p.setFillColorRGB(0.3, 0.3, 0.3)
    p.drawString(margin, info_box_y, "INVOICE #")
    p.drawString(margin, info_box_y - 18, "DATE")
    p.drawString(margin, info_box_y - 36, "DUE DATE")
    
    p.setFont("Helvetica", 9)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(margin + 80, info_box_y, order.order_number)
    p.drawString(margin + 80, info_box_y - 18, order.created_at.strftime('%m/%d/%Y'))
    p.drawString(margin + 80, info_box_y - 36, order.created_at.strftime('%m/%d/%Y'))
    
    y -= 80

    # ================= BILL TO / SHIP TO SECTIONS =================
    y -= 30
    
    # Bill To section
    p.setFont("Helvetica-Bold", 10)
    p.setFillColorRGB(0.42, 0.22, 0.58)
    p.drawString(margin, y, "BILL TO:")
    
    p.setFont("Helvetica", 10)
    p.setFillColorRGB(0, 0, 0)
    y -= 18
    
    if billing:
        p.setFont("Helvetica-Bold", 11)
        p.drawString(margin, y, f"{billing.first_name} {billing.last_name}")
        p.setFont("Helvetica", 9)
        y -= 14
        p.drawString(margin, y, billing.address_line_1)
        if billing.address_line_2:
            y -= 12
            p.drawString(margin, y, billing.address_line_2)
        y -= 12
        p.drawString(margin, y, f"{billing.city}, {billing.state}")
        y -= 12
        p.drawString(margin, y, f"{billing.country} - {billing.pincode}")
        y-=12
        p.drawString(margin,y, f"Phone: {billing.phone}")
    else:
        p.drawString(margin, y, "No billing address provided")
    
    # Ship To section (right side)
    ship_y = y + 74  # Reset to same starting y as Bill To
    p.setFont("Helvetica-Bold", 10)
    p.setFillColorRGB(0.42, 0.22, 0.58)
    p.drawString(width/2 + 20, ship_y, "SHIP TO:")
    
    p.setFont("Helvetica", 10)
    p.setFillColorRGB(0, 0, 0)
    ship_y -= 18
    
    p.setFont("Helvetica-Bold", 11)
    p.drawString(width/2 + 20, ship_y, f"{order.first_name} {order.last_name}")
    p.setFont("Helvetica", 9)
    ship_y -= 14
    p.drawString(width/2 + 20, ship_y, order.address_line_1)
    if order.address_line_2:
        ship_y -= 12
        p.drawString(width/2 + 20, ship_y, order.address_line_2)
    ship_y -= 12
    p.drawString(width/2 + 20, ship_y, f"{order.city}, {order.state}")
    ship_y -= 12
    p.drawString(width/2 + 20, ship_y, f"{order.country} - {order.pincode}")
    ship_y -= 12
    p.drawString(width/2 + 20, ship_y, f"Phone: {order.phone}")

    # ================= ITEMS TABLE =================
    y -= 100
    
    # Table header with purple background
    p.setFillColorRGB(0.93, 0.93, 0.95)  # Light gray background
    p.rect(margin, y - 20, width - 2*margin, 20, fill=1, stroke=0)
    
    p.setFillColorRGB(0.2, 0.2, 0.2)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(margin + 5, y - 13, "ITEMS")
    p.drawString(margin + 200, y - 13, "DESCRIPTION")
    p.drawRightString(width - margin - 140, y - 13, "QTY")
    p.drawRightString(width - margin - 70, y - 13, "PRICE")
    p.drawRightString(width - margin - 5, y - 13, "AMOUNT")
    
    y -= 35
    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica", 9)
    
    # Draw items
    for idx, item in enumerate(items):
        # Alternate row coloring
        if idx % 2 == 0:
            p.setFillColorRGB(0.98, 0.98, 0.98)
            p.rect(margin, y - 10, width - 2*margin, 24, fill=1, stroke=0)
        
        p.setFillColorRGB(0, 0, 0)
        
        # Product name
        product_name = item.product.product_name
        if len(product_name) > 25:
            product_name = product_name[:22] + "..."
        p.drawString(margin + 5, y, product_name)
        
        # Variations as description
        variations = [
            f"{v.variation_category}: {v.variation_value}"
            for v in item.variations.all()
        ]
        if variations:
            desc = ", ".join(variations)
            if len(desc) > 35:
                desc = desc[:32] + "..."
        else:
            desc = "No variation"
        
        p.setFont("Helvetica", 8)
        p.drawString(margin + 200, y, desc)
        p.setFont("Helvetica", 9)
        
        # Quantity, Price, Amount
        p.drawRightString(width - margin - 140, y, str(item.quantity))
        p.drawRightString(width - margin - 70, y, f"${item.product_price:.2f}")
        p.drawRightString(width - margin - 5, y, f"${item.subtotal():.2f}")
        
        y -= 24
    
    # Separator line
    y -= 10
    p.setStrokeColorRGB(0.8, 0.8, 0.8)
    p.setLineWidth(0.5)
    p.line(margin, y, width - margin, y)

    # ================= TOTALS SECTION =================
    y -= 30
    
    # Right-aligned totals
    totals_x = width - margin - 70
    amounts_x = width - margin - 5
    
    p.setFont("Helvetica", 10)
    p.setFillColorRGB(0.3, 0.3, 0.3)
    
    p.drawRightString(totals_x, y, "Subtotal:")
    p.setFillColorRGB(0, 0, 0)
    p.drawRightString(amounts_x, y, f"${order.total():.2f}")
    
    y -= 16
    p.setFillColorRGB(0.3, 0.3, 0.3)
    p.drawRightString(totals_x, y, "Tax:")
    p.setFillColorRGB(0, 0, 0)
    p.drawRightString(amounts_x, y, f"${order.tax:.2f}")
    
    # Total amount with purple background
    y -= 25
    p.setFillColorRGB(0.42, 0.22, 0.58)
    p.rect(width - margin - 180, y - 5, 180, 25, fill=1, stroke=0)
    
    p.setFillColorRGB(1, 1, 1)
    p.setFont("Helvetica-Bold", 14)
    p.drawRightString(totals_x, y + 3, "TOTAL")
    p.drawRightString(amounts_x, y + 3, f"${order.order_total:.2f}")

    # ================= FOOTER =================
    p.setFillColorRGB(0.5, 0.5, 0.5)
    p.setFont("Helvetica-Oblique", 8)
    p.drawCentredString(width / 2, 40, "Thank you for your business!")
    p.setFont("Helvetica", 7)
    p.drawCentredString(width / 2, 28, "This invoice was generated automatically by BlazeKart.")

    p.showPage()
    p.save()
    return response


@login_required
def change_order_address(request,order_number):
    order=get_object_or_404(Order,order_number=order_number,user=request.user,is_ordered=True)

    if order.status in ['completed','cancelled','shipped']:
        messages.error(request, "Address cannot be changed for this order.")
        return redirect('order_details', order_num=order_number)
    
    addresses=UserAddress.objects.filter(user=request.user)

    if request.method == "POST":
        addr=get_object_or_404(UserAddress,id = request.POST.get('address_id'))

        order.first_name=addr.first_name
        order.last_name=addr.last_name
        order.phone=addr.phone
        order.address_line_1=addr.address_line_1
        order.address_line_2=addr.address_line_2
        order.city=addr.city
        order.state=addr.state
        order.country=addr.country
        order.pincode=addr.pincode
        order.save()

        messages.success(request,"Order address updated successfully.")
        return redirect('order_details',order.order_number)
    
    return render(request,'dashboard/change_order_address.html',{'order':order,'addresses':addresses})

@login_required
def cancel_order(request,order_number):
    order=get_object_or_404(Order,order_number=order_number,user=request.user,is_ordered=True)

    if order.status in ['completed','cancelled','shipped']:
        messages.error(request, "This order cannot be cancelled.")
        return redirect('order_details', order_num=order_number)
    
    order_items=OrderItem.objects.filter(order=order)

    for item in order_items:
        product=item.product
        product.stock+=item.quantity
        product.save()

    order.status='Cancelled'
    order.save()

    messages.warning(request, "Your order has been cancelled.")
    return redirect('order_details', order_num=order_number)


def help_support(request):
    return render(request,'dashboard/help_support.html')





def logout(request):
    auth.logout(request)
    list(messages.get_messages(request))
    messages.warning(request,'You Have Log-out, Please Log-In')
    return redirect('login')




@login_required
def profile(request):
    user=request.user
    profile,created=UserProfile.objects.get_or_create(user=user)
    addresses=UserAddress.objects.filter(user=request.user)
    wishlists=WishList.objects.filter(user=request.user)
    orders=Order.objects.filter(user=request.user,is_ordered=True)
    cartitems=CartItem.objects.filter(user=request.user)
    address_count=addresses.count()
    wishlist_count=wishlists.count()
    order_count=orders.count()
    cartitems_count=cartitems.count()


    if request.method == "POST" and request.FILES.get('profile_pic'):
        image = request.FILES['profile_pic']

        if image.size > 2 * 1024 * 1024:
            messages.error(request, "Profile picture must be under 2MB")
            return redirect('profile')

        profile.profile_pic = image
        profile.save()
        messages.success(request, "Profile picture updated")
        return redirect('profile')
    

    if request.method == "POST" and 'remove_pfp' in request.POST:
        if profile.profile_pic:
            profile.profile_pic.delete(save=False)  # delete file
            profile.profile_pic = None               # reset DB field
            profile.save()
        return redirect('profile')


    if request.method=="POST" and 'personal_info_form' in request.POST:
        user.first_name=request.POST.get('first_name',user.first_name)
        user.last_name=request.POST.get('last_name',user.last_name)
        user.username=request.POST.get('username',user.username)
        user.save()

        dob=request.POST.get('DOB') 
        if dob:
            profile.date_of_birth=dob 
        gender=request.POST.get('gender',profile.gender)
        if gender:
            profile.gender=gender
        profile.save()
        messages.success(request, "Personal information updated")
        return redirect('profile')
    

    if request.method=="POST" and 'contact_bio_form' in request.POST:
        user.email=request.POST.get('email',user.email)
        user.phone_no=request.POST.get('phone_no',user.phone_no)
        user.save()

        profile.bio=request.POST.get('bio',profile.bio)
        profile.save()
        messages.success(request, "Contact and bio updated")
        return redirect('profile')
    


    if request.method=="POST" and request.POST.get('edit_address_id'):
        address_id=request.POST.get('edit_address_id')
        address= UserAddress.objects.get(id=address_id,user=request.user)

        if request.POST.get('is_default'):
            UserAddress.objects.filter(user=request.user).update(is_default=False)
            address.is_default=True
        else:
            address.is_default=False

        address.first_name = request.POST.get('first_name')
        address.last_name = request.POST.get('last_name')
        address.phone = request.POST.get('phone')
        address.address_line_1 = request.POST.get('address_line_1')
        address.address_line_2 = request.POST.get('address_line_2')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.country = request.POST.get('country')
        address.pincode = request.POST.get('pincode')
        address.label = request.POST.get('label')

        address.save()

        messages.success(request, "Address updated successfully")
        return redirect('profile')
    

    if request.method=="POST" and 'add_address_form' in request.POST:

        existing_addresses=UserAddress.objects.filter(user=request.user)
        is_default=False

        if request.POST.get('is_default'):
            existing_addresses.update(is_default=False)
            is_default=True

        if not existing_addresses.exists():
            is_default=True
        
        UserAddress.objects.create(
            user=request.user,
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            phone=request.POST.get('phone'),
            address_line_1=request.POST.get('address_line_1'),
            address_line_2=request.POST.get('address_line_2'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            country=request.POST.get('country'),
            pincode=request.POST.get('pincode'),
            label=request.POST.get('label'),
            is_default=is_default
        )
        messages.success(request, "Address added successfully")

        next_url=request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('profile')
    

    if request.method=="POST" and "set_default_address" in request.POST:
        address_id=request.POST.get('set_default_address')

        UserAddress.objects.filter(user=request.user).update(is_default=False)

        UserAddress.objects.filter(id=address_id,user=request.user).update(is_default=True)
        messages.info(request, "Default address updated")
        return redirect('profile')
    

    if request.method=="POST" and 'delete_address' in request.POST:
        address_id=request.POST.get('delete_address')

        address=UserAddress.objects.filter(id=address_id,user=request.user)
        address.delete()
        messages.error(request, f" Address was deleted ")
        return redirect('profile')

    context={
        'profile':profile,
        'addresses':addresses,
        'address_count':address_count,
        'order_count':order_count,
        'wishlist_count':wishlist_count,
        'cartitems_count':cartitems_count,
    }

    return render(request,'dashboard/profile.html',context)

@login_required
def enable_2fa(request):
    profile=request.user.profile

    if profile.two_factor_enabled:
        messages.info(request,"Two-factor authentication already enabled.")
        return redirect('profile')
    
    device,created=TOTPDevice.objects.get_or_create(user=request.user,name='default')

    if request.method == "POST":
        otp=request.POST.get('otp')
        if device.verify_token(otp):
            profile.two_factor_enabled=True
            profile.save()
            messages.success(request, "Two-factor authentication enabled.")
            return redirect('profile')
        else:
            messages.error(request, "Invalid OTP code.")

    return render(request,'dashboard/enable_2fa.html',{'qr_code':device.config_url})


def payments_methods(request):
    return render(request,'dashboard/payments_methods.html')