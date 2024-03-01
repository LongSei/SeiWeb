from django.shortcuts import render, redirect
from django.http import JsonResponse
from carts.models import CartItem
from .forms import OrderForm, OrderPaymentForm
import datetime
from django.contrib import messages
from .models import Order, Payment, OrderProduct
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def sendEmail(request, order):
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()


def payments(request):
    if request.method == "POST":
        form = OrderPaymentForm(request.POST)
        if form.is_valid(): 
            [payment_method, order_number]= request.POST['paymentQuery'].split("!")
            payment = Payment()
            order = Order.objects.get(order_number=order_number)
            payment.user = order.user
            payment.payment_id = request.POST['paymentQuery']
            payment.payment_method = payment_method
            payment.amount_paid = 0
            payment.status = 'Chưa thanh toán'
            payment.created_at = order.created_at
            payment.save()
            order.payment = payment
            order.save()
            cart_items = CartItem.objects.filter(user=order.user)
            for item in cart_items: 
                order_product = OrderProduct()
                order_product.order = order
                order_product.payment = payment
                order_product.user = order.user
                order_product.product = item.product
                order_product.quantity = item.quantity
                order_product.product_price = item.product.price
                order_product.ordered = True
                order_product.created_at = order.created_at
                order_product.save()

                product = Product.objects.get(id=item.product.id)
                product.stock -= item.quantity
                product.sold += item.quantity
                product.save()

            CartItem.objects.filter(user=request.user).delete()
            Order.objects.filter(payment=None).delete()
            messages.success(
                request=request, 
                message="Đơn hàng đã được ghi lại để xử lí !!!"
            )
            return redirect('home')


def place_order(request, total=0, quantity=0,):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    grand_total = total 

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.Name = form.cleaned_data['Name']
            data.Phone = form.cleaned_data['Phone']
            data.Email = form.cleaned_data['Email']
            data.Address = form.cleaned_data['Address']
            data.Note = form.cleaned_data['Note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")     # 20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)

    else:
        return redirect('checkout')

def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except Exception:
        return redirect('home')