
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Accounts, UserProfile
from .forms import RegistrationForm, UserForm, UserprofileForm 
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from django.db.models import Q 


#  verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import requests

from cart.views import _cart_id
from cart.models import Cart,CartItem


from orders.models import Order, OrderProduct

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            
            user = Accounts.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()
            
            #user activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your accounts'
            message = render_to_string('accounts/account_verification_email.html',{
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            
            
            messages.success(request, 'Thank you for registering with us. we have sent you verification email to your email address, please verify')
            return redirect('/accounts/login/?command=verification&email='+email)
            # return redirect('login')
    else:
        form = RegistrationForm()
    
    context = {
         'form':form,
    }
    return render(request,'accounts/register.html',context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        user = auth.authenticate(email=email, password=password)
        
        if user is not None:
            try:
                # print('entering inside try block')
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                # print(is_cart_item_exists)
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    # print(cart_item)
                    
                    # getting the product variations by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # Getting the cart items from thr user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    # product_variation = [1,2,3,4,6]
                    # ex_var_list = [4,6,3,5]
                    
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()

                    # for item in cart_item:
                        # item.user = user
                        # item.save()
            except:
                # print('entering inside except block')
                pass
            auth.login(request, user)
            messages.success(request, "You are now logged in.")
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                print('query ->',query)
                print('-----------')
                # next=/cart/checkout
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('home')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')



@login_required(login_url = 'login' )
def logout(request):
    auth.logout(request)
    messages.success(request,'You are now logged out .')
    return redirect('login')



def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Accounts._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Accounts.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        
        # Userprofile generation
        user_profile = UserProfile.objects.create(
            user = user,
        )
        user_profile.save()

        messages.success(request,'Congratulations! Your account is activated. ')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')


@login_required(login_url = "login")
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()
    check = UserProfile.objects.filter(user_id=request.user.id)
    
    userprofile = UserProfile.objects.get(user_id=request.user.id)
    context = {
            'orders_count' : orders_count,
            'userprofile' : userprofile,
        }
    return render(request, 'accounts/dashboard.html', context)
    



def ForgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Accounts.objects.filter(email=email).exists():
            user = Accounts.objects.get(email__iexact=email)
          
            #Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html',{
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()  
            
            messages.success(request, ' Password reset has been sent to your email address.')
            return redirect('login')  
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('ForgotPassword')
            
    return render(request, 'accounts/ForgotPassword.html') 



def resetpassword_validate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Accounts._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Accounts.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid']=uid
        messages.success(request,'please reset your password ')
        return redirect('resetpassword')
    else:
        messages.error(request,'this link has been expired!')
        return redirect('login')



def resetpassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST.get('confirm_password')
        
        if password == confirm_password:
            uid=request.session.get('uid')
            user=Accounts.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'password reset is successfull')
            return redirect('login')
            
        else:
            messages.error(request,'password do not match!')
            return redirect('resetpassword')
        
    else:
        return render(request,'accounts/resetpassword.html')



def my_orders(request):
    orders = Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    context = {
        'orders':orders,
    }
    return render(request, 'accounts/my_orders.html',context)


@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserprofileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserprofileForm(instance=userprofile)
    context = {
        'user_form':user_form,
        'profile_form':profile_form,
        'userprofile':userprofile,
    }
    return render(request,'accounts/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        
        user = Accounts.objects.get(username__exact=request.user.username)
        
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('login')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
                
        else:
            messages.error(request, 'Password does no match!')
            return redirect('change_password')
    return render(request,'accounts/change_password.html')



@login_required(login_url='login')
def order_detail(request,order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    total = 0
    tax = 0
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
        
    tax = (2*total) / 100
    grand_total = total + tax
    context = {
        'order_detail':order_detail,
        'order':order,
        'total':total,
        'tax':tax,
        'subtotal':subtotal
    }
    return render(request,'accounts/order_detail.html',context)


def user_manage_order(request):
      if request.user.is_admin:
            if request.method == 'POST':
                keyword = request.POST['keyword']
                orders = Order.objects.filter(Q(is_ordered=True), Q(order_number__icontains=keyword) | Q(user__email__icontains=keyword) | Q(firstname__icontains=keyword) | Q(lastname__icontains=keyword)).order_by('-order_number')
    
            else:
                orders = Order.objects.filter(is_ordered=True).order_by('-order_number')
      
            paginator = Paginator(orders, 10)
            page = request.GET.get('page')
            paged_orders = paginator.get_page(page)
            context = {
            'orders': paged_orders
            }
            return render(request, 'accounts/my_orders.html', context)
  
      else:
            return redirect('home')



@login_required(login_url='login')
def user_cancel_order(request, order_number):
    order = Order.objects.get(order_number=order_number)
    order.status = 'Order Cancelled'
    order.save()
        
    return render(request, 'accounts/cancel_message.html')
  
       

