from django.http import JsonResponse
from django.shortcuts import redirect, render
from cart.admin import CartItemAdmin
from cart.models import CartItem
from orders.models import Order
from store.models import Product
from .models import Coupon, OrderProduct, Payment
from .forms import OrderForm
import datetime

from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.contrib import messages

import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
# from django.http import HttpResponseBadRequest
from proj import settings
from django.utils import timezone


# Create your views here.

@login_required(login_url='login')
@csrf_exempt
def payment(request, total=0):
  current_user = request.user
  cart_item = CartItem.objects.filter(user=current_user)
  
  tax = 0
  grand_total = 0
  
  for item in cart_item:
    total += (item.product.price * item.quantity)
    
  tax = (2 * total) / 100
  grand_total = total + tax
  
  order_number = request.session['order_number']
  order = Order.objects.get(user=current_user, is_ordered=False,order_number = order_number)
    
  
  currency = 'INR'
  razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

  response_payment  = razorpay_client.order.create(dict(amount=int(grand_total) * 100,currency=currency))
  order_id = response_payment['id']
  order_status = response_payment['status']
  if order_status == 'created':
    payDetails = Payment(
      user = current_user,
      order_id = order_id,
      order_number = order_number,
      amount_paid = grand_total 
    )
    payDetails.save()

    
  context = {
      'order': order,
      'cart_items': cart_item,
      'total': total,
      'tax': tax,
      'grand_total': grand_total,
      
      'payment': response_payment,
      'razorpay_merchant_key':settings.RAZOR_KEY_ID,
      'grand_total': grand_total,
  }
  return render(request, 'orders/payment.html', context)


def place_order(request, quantity=0, total=0):
    current_user = request.user


    cart_items =CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count < 0:
        return redirect('store')

    grand_total = 0
    tax  = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax

    
    if request.method == 'POST':
        form = OrderForm(request.POST)

        # print(form)
        
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.country = form.cleaned_data['country']
            data.pincode = form.cleaned_data['pincode']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Generate Order number
            year = int(datetime.date.today().strftime('%Y'))
            month = int(datetime.date.today().strftime('%m'))
            date = int(datetime.date.today().strftime('%d'))
            d = datetime.date(year, month, date)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            # context = {
            #     'order' : order,
            #     'cart_items' : cart_items,
            #     'total' : total,
            #     'tax' : tax,
            #     'grand_total' : grand_total,
            # }
            # return render(request, 'orders/payment.html', context)
            request.session['order_number'] = order_number
            print(f"order no : ${request.session['order_number']}")
            return redirect('payment')
    
        else:
            return redirect('checkout')


def payment_success(request):
    order_number = request.session['order_number']
    transaction_id = Payment.objects.get(order_number=order_number)
  
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        
        # Change order status to Accepted when order is success
        order.status = 'Order Accepted'
        order.save()
        
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        
        tax = 0
        total = 0
        grand_total = 0
        
        for item in ordered_products:
            total += (item.product_price * item.quantity)
        
        tax = (2*total ) / 100
        grand_total = total + tax
        
        #Order Confirmmation Mail
        
        current_site = get_current_site(request)
        mail_subject = "Order Confirmation"
        message = render_to_string('orders/order_confirmation.html', {
        'order': order,
        'domain': current_site
        })
        to_mail = order.user.email
        send_email = EmailMessage(mail_subject, message, to=[to_mail])
        send_email.send()
        messages.success(request, 'Order confirmation mail has been send to your registered email address')

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'transaction_id': transaction_id,
            'total': total,
            'tax': tax,
            'grand_total': grand_total
        }
        
        return render(request, 'orders/success.html', context)
    
    except Exception as e:
        raise e

def payment_fail(request):
  return render(request, 'orders/fail.html')



@csrf_exempt
def payment_status(request):
    response = request.POST
    params_dict = {
        'razorpay_order_id': response['razorpay_order_id'],
        'razorpay_payment_id': response['razorpay_payment_id'],
        'razorpay_signature': response['razorpay_signature']
    }
    
    
    # authorize razorpay client with API Keys.
    razorpay_client = razorpay.Client(
      auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    client = razorpay_client
    try:
      status = client.utility.verify_payment_signature(params_dict)
      transaction = Payment.objects.get(order_id=response['razorpay_order_id'])
      transaction.status = status
      transaction.payment_id = response['razorpay_payment_id']
      transaction.save()
      
      # get order number
      order_number = transaction.order_number
      order = Order.objects.get(is_ordered=False, order_number=order_number)
      
      order.payment = transaction
      order.is_ordered = True
      order.save()
      
      cart_items = CartItem.objects.filter(user=order.user)
      for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.payment = transaction
        order_product.user_id = order.user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity 
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()
        
        # Reducing Stock
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
        
        #  Clearing Cart Items
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variation.set(product_variation)
        order_product.save()
      
      CartItem.objects.filter(user=order.user).delete()
      
      return redirect('payment_success')
    
    except Exception as e:
      # raise e
      transaction = Payment.objects.get(order_id=response['razorpay_order_id'])
      transaction.delete()
      return redirect('payment_fail')



# COUPEN 

@login_required(login_url='login')
def apply_coupon(request):
    coupon_code = request.GET['coupon_code']
    if Coupon.objects.filter(coupon_code__exact=coupon_code, is_active=True).exists():
        coupon = Coupon.objects.filter(coupon_code__exact=coupon_code, is_active=True)
        order_number = request.session['order_number']
        order = Order.objects.get(order_number=order_number)
        print('ABOVE THE ERROR================================================')
        if not Order.objects.filter(user=request.user, coupon=coupon[0]):
            print('THE COUPON DOESNOT USED================================================================================')
            if coupon.filter(expiry_at__gte=timezone.now()):
                if order.order_total > coupon[0].minimum_amount:
                    print('THIS IS MORETHAN MINIMUM AMOUNT')
                    order.coupon = coupon[0]
                    print(order.coupon)
                    order.coupon_discount = coupon[0].discount_price
                    print(order.coupon_discount)
                    order.order_total -= coupon[0].discount_price
                    print(order.order_total)
                    order.save()
                    messages = "Coupon is Applied"
                    print(messages)
                    current_user = request.user
                    cart_items = CartItem.objects.filter(user=current_user)
                    tax = 0
                    grand_total = 0
                    for cart_item in cart_items:
                        grand_total += (cart_item.product.price *
                                         cart_item.quantity)
                    tax = (2*grand_total)/100
                    sub_total = grand_total-tax
                    coupon_discount = coupon[0].discount_price
                    grand_total -= coupon_discount

                    context = {
                        'order': order,
                        'cart_items': cart_items,
                        'grand_total': grand_total,
                        'tax': tax,
                        'sub_total': sub_total,
                        'coupon_discount': coupon_discount
                    }

                    t = render_to_string('orders/renderpayment.html', context)
                    print(" THIS IS BLELOW THE T")
                    return JsonResponse({'data': t, 'msg': messages})

                else:
                    messages = "You need to purchase minimum amount of " + str(coupon[0].minimum_amount) + " to apply this coupon"
                    return JsonResponse({'msg': messages})
            else:
                messages = "Coupon is Expired"
                return JsonResponse({'msg': messages})
        else:
            print('THE COUPON IS ALREADY IS USED')
            messages = "Coupon is Already is used"
            return JsonResponse({'msg': messages})
    else:
        messages = "Coupon is Invalid"
        return JsonResponse({'msg': messages})