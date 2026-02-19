from django.shortcuts import render,redirect
from .models import Account
from .forms import RegistrationForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import re
from cart.models import Cart,CartItem
from cart.views import _cart_id
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone 
from django.conf import settings
# Create your views here.
def register(request):

    if request.method=="POST":
        form=RegistrationForm(request.POST)
        if form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            phone_no=form.cleaned_data['phone_no']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            username=email.split('@')[0]

            errors=[]

            password_errors=validate_password(password)
            errors.extend(password_errors)
           
            if errors:
                # return redirect('register')
                return render(request,'accounts/register.html',{'errors':errors,'form':form})
             
            else:
                user=Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)
                user.phone_no=phone_no
                if Account.objects.filter(email=email):
                    pass
                else:
                    user.save()
                messages.success(request,'Please Verify Your Email For Account Activation! ')

                #Email sending all verigy part
                current_site=get_current_site(request)
                mail_subject="Welcome to BlazeKart! Activate Your Account"
                message=render_to_string('accounts/account_verification_email.html',
                                        {'user':user,
                                        'domain':current_site,
                                        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                                        'token':default_token_generator.make_token(user)})
                to_email=email
                send_mail=EmailMessage(mail_subject,message,from_email=settings.DEFAULT_FROM_EMAIL,to=[to_email],reply_to=[settings.SUPPORT_EMAIL],)
                send_mail.content_subtype = "html"
                send_mail.send()
                 
                 
    else:
        form=RegistrationForm()
    context={
        'form':form,
    }


    return render(request,'accounts/register.html',context)

def validate_password(password):
            errors=[]
    
            if len(password)<8:
                print(f'password is 8 atleast:{password}')
                errors.append("At least 8 Character")

            if not re.search(r"[A-Z]+",password):
                print(f'password have a capital letter:{password} ')
                errors.append("One Capital Letter")

            if not re.search(r'\d+',password):
                print(f'ek digit h atleast:{password}')
                errors.append("One number")

            if not re.search(r'[\W_]',password):
                print(f'kuch naya h :{password}')
                errors.append("One Special Character.")

            if not re.search(r"[a-z]+",password):
                print(f'pasword contain valid character:{password}')
                errors.append("Please use Valid Characters.")
        
            return errors


def activate(request,uid,token):
    try:
        uid=urlsafe_base64_decode(uid).decode()
        print(f'yaha aya uid: {uid}')
        user=Account._default_manager.get(pk=uid)
        print(f'user:{user}')
    except Exception:
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.info(request,"Email verified. Redirected to Log-In...")
        return redirect('login')
    else:
        messages.error(request,"Registeration Failed! Try Again!")
        return redirect('register')


def login(request):

    if request.method=="POST":
        email=request.POST['email']
        password=request.POST['password']
        user=auth.authenticate(email=email,password=password)
        if user is not None:
            try:
                cart=Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists=CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item=CartItem.objects.filter(cart=cart,is_active=True)
                    product_variation=[]
                    for item in cart_item:
                        variation=item.variations.all()
                        product_variation.append(list(variation))

                    cart_item=CartItem.objects.filter(user=user)
                    ex_var_list=[]
                    id=[]
                    for item in cart_item:
                        variation=item.variations.all()
                        ex_var_list.append(list(variation))
                        id.append(item.id)
                    
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index=ex_var_list.index(pr)
                            item_id=id[index]
                            item=CartItem.objects.get(id=item_id)
                            item.quantity+=1
                            item.user=user
                            item.save()
                        else:
                            cart_item=CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user=user
                                item.save()
            except:
                pass



            auth.login(request,user)
            messages.success(request,"Login Successful. Redirecting to Home Page....")
            return render(request,'accounts/login.html',{'redirect_home':True})
        else:
            messages.error(request,'Email And Password Does Not Match!')
            return render(request,'accounts/login.html')

    return render(request,'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    list(messages.get_messages(request))
    messages.warning(request,'You Have Log-out, Please Log-In')
    return redirect('login')


def forgotpassword(request):
    if request.method=="POST":
        email=request.POST['email']

        if Account.objects.filter(email=email).exists():
            user=Account.objects.get(email__iexact=email)
            current_site=get_current_site(request)
            mail_subject="Please Verify Your account"
            message=render_to_string('accounts/reset_password_email.html',
                                      {'user':user,
                                       'domain':current_site,
                                       'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                                       'token':default_token_generator.make_token(user)})
            to_email=email
            send_mail=EmailMessage(mail_subject,message,to=[to_email])
            send_mail.send()
            messages.info(request,'Check Your Email To Reset Password!')
            return render(request,'accounts/forgotpassword.html')
        else:
            messages.warning(request,"Email Not Found! ")
            return render(request,'accounts/forgotpassword.html')
    return render(request,'accounts/forgotpassword.html')


def reset_password_validate(request,uid,token):
    try:
        uid=urlsafe_base64_decode(uid).decode()
        print(f'yaha aya uid: {uid}')
        user=Account._default_manager.get(pk=uid)
        print(f'user:{user}')
    except Exception:
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid']=uid
        messages.info(request,'Email Verified!')
        return render(request,'accounts/resetpassword.html',{'redirect_login':True})
    else:
        messages.warning(request,'Something Goes Wrong!')
        return render(request,'accounts/login.html')
    

def reset_password(request):
    if request.method=="POST":
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        if password==confirm_password:
            uid=request.session.get('uid')
            user=Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,"Password is Changed Successful. Redirecting to Log-In...")
            return render(request,'accounts/resetpassword.html',{'redirect_login':True})
        else:
            messages.warning(request,'password does not match!')
            return render(request,'accounts/resetpassword.html')

    return render(request,'accounts/resetpassword.html')


@login_required
def change_password(request):
    if request.method=="POST":
        form = PasswordChangeForm(request.user,request.POST)
        if form.is_valid():
            user=form.save()
            auth.update_session_auth_hash(request,user)

            profile=request.user.profile
            profile.password_updated_at=timezone.now()
            profile.save()

            messages.success(request,'Password updated successfully')
        else:
            for error in form.errors.values():
                messages.error(request,error)
    
    return redirect('profile')


def signin(request):
    if not request.user.is_authenticated:
        messages.info(request,'Please Sign-in for smooth experience.')
        return render(request,'accounts/login.html')