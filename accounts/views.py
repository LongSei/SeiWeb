from re import split
from carts.models import Cart, CartItem
from django.shortcuts import redirect, render
from django.contrib import messages, auth
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.tokens import default_token_generator
from .forms import RegistrationForm, UploadProductsForm, ProfileChangeForm, MultipleImageUploadForm
from accounts.models import Account
from orders.models import Order, Payment, OrderProduct
from store.models import Product, ImageSet, ImageModel
from carts.views import _cart_id
from category.models import Category
from django.db import models
from django.template import loader

import requests
from django.db.models import F, Q, FloatField


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            user = Account.objects.create_user(
                name=name, email=email, username=username, password=password)
            user.phone_number = phone_number

            current_site = get_current_site(request=request)
            mail_subject = 'Activate your blog account.'
            context = {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            }
            message = render_to_string('accounts/active_email.html', context)

            send_email = EmailMessage(mail_subject, message, to=[email])
            send_email.content_subtype = 'html'
            send_email.send()
            messages.success(
                request=request,
                message="Kích hoạt tài khoản bằng đường dẫn đã được gửi qua email"
            )
            user.save()
            return redirect('login')
        else:
            messages.error(request=request, message="Register failed!")
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_items = CartItem.objects.filter(cart=cart)
                if cart_items.exists():
                    cart_items = CartItem.objects.filter(user=user)
            except Exception:
                pass
            auth.login(request=request, user=user)
            messages.success(request=request, message="Đăng nhập thành công!")
            return redirect('home')
        else:
            messages.error(request=request, message="Đăng nhập không thành công!")
    context = {
        'email': email if 'email' in locals() else '',
        'password': password if 'password' in locals() else '',
    }
    return render(request, 'accounts/login.html', context=context)


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request=request, message="Bạn đã đăng xuất!")
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except Exception:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request=request, message="Tài khoản đã kích hoạt, Vui lòng đăng nhập !")
        return render(request, 'accounts/login.html')
    else:
        messages.error(request=request, message="Đường dẫn không hợp lệ !")
        return redirect('home')

def change_profile(request, uidb64, token, email, phone_number):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except Exception:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.email = email
        user.phone_number = phone_number
        user.save()
        messages.success(
            request=request, message="Tài khoản đã được đổi thông tin, từ giờ mọi thông báo sẽ được liên hệ qua thông tin mới !!!")
        return render(request, 'accounts/login.html')
    else:
        messages.error(request=request, message="Lỗi xảy ra khi đổi thông tin !!!")
        return redirect('home')


@login_required(login_url="login")
def orderHistory(request):
    user = Account.objects.get(email=request.user.email)
    orders = Order.objects.filter(user=user).order_by('-created_at')
    order_products = OrderProduct.objects.annotate(total_value=models.ExpressionWrapper(models.F('quantity') * 1.0 * models.F('product_price'), output_field=models.FloatField())).filter(user=user)
    return render(request, "accounts/orderHistory.html", {'orders': orders, 'order_products': order_products})

@login_required(login_url="login")
def profile(request):
    user = Account.objects.get(email=request.user.email)
    if request.method == "POST":
        form = ProfileChangeForm(request.POST)
        if form.is_valid():
            user=Account.objects.get(email=request.user.email)
            user.name = form.cleaned_data['name']
            user.email = form.cleaned_data['email']
            user.phone_number = form.cleaned_data['phone_number']
            exists_user = Account.objects.filter(email=form.cleaned_data['email']).exclude(email=request.user.email).exists()
            if (user.is_superadmin):
                user.save()

            elif (exists_user != True):
                current_site = get_current_site(request=request)
                mail_subject = 'Đổi thông tin tài khoản'
                message = render_to_string('accounts/change_profile_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                    'email': form.cleaned_data['email'],
                    'phone_number': form.cleaned_data['phone_number']
                })
                send_email = EmailMessage(mail_subject, message, to=[request.user.email])
                send_email.send()
                messages.success(
                    request=request,
                    message="Vui lòng xác nhận email để đổi thông tin"
                )
            else:
                messages.error(request, "Email mới của bạn trùng với một tài khoản khác")

        return redirect('profile')
    total_income = 0
    for product in Product.objects.filter(user=user):
        total_income += product.sold * product.price
    products = Product.objects.filter(user=user).annotate(percent_income=models.ExpressionWrapper(models.F('sold') * 1.0 * models.F('price') / float(total_income) * 100.0, output_field=models.FloatField()),
                                                        total_income=models.ExpressionWrapper(models.F('sold') * models.F('price'), output_field=models.FloatField()))
    return render(request, "accounts/profile.html", {'user': user, 'sold_products': products, 'total_income': total_income})

@login_required(login_url='login')
def storeHistory(request):
    if request.user.is_superadmin == True:
        products = Product.objects.filter(user=Account.objects.get(email=request.user.email)).order_by('-created_date')
        return render(request, "accounts/storeHistory.html", {'products': products})

@login_required(login_url='login')
def deleteProducts(request, product_id):
    if request.user.is_superadmin == True:
        Product.objects.get(id=product_id).delete()
        return redirect('storeHistory')

@login_required(login_url='login')
def soldHistory(request):
    if request.user.is_superadmin == True:
        pending_orders = Order.objects.all().filter(~Q(status="Huỷ bỏ")).order_by('-created_at')
        order_products = (OrderProduct.objects.all().annotate(total_value=models.ExpressionWrapper(models.F('quantity') * 1.0 * models.F('product_price'), output_field=models.FloatField())))
        return render(request, 'accounts/soldHistory.html', {'pending_orders': pending_orders, 'order_products': order_products})

@login_required(login_url='login')
def editOrder(request, order_number, method):
    if request.user.is_superadmin == True:
        order = Order.objects.get(order_number=order_number)
        if (method == "delete"):
            order_products = OrderProduct.objects.filter(order=order)
            for product in order_products:
                instance = Product.objects.get(product_name=product.product.product_name)
                instance.stock += product.quantity
                instance.sold -= product.quantity
                instance.save()
            order.delete()
        if (method == "progress"):
            if (order.status == "Đang xử lí"):
                order.status = "Đang đóng gói và giao hàng"
            elif (order.status == "Đang đóng gói và giao hàng"):
                order.status = "Hoàn thành"
            order.save()
        return redirect('soldHistory')

@login_required(login_url="login")
def uploadProducts(request, product_id=None):
    categories = Category.objects.all()
    imageForm = MultipleImageUploadForm()
    if request.method == "POST" and request.user.is_superadmin == True:
        data = request.POST.copy()
        data['category'] = Category.objects.get(category_name=request.POST['category'])
        data['stock'] = int(data['stock'])
        data['price'] = int(data['price'])
        if (product_id != None):
            data['product_name'] = "@" + data['product_name']
        dataForm = UploadProductsForm(data)
        if dataForm.is_valid():
            if product_id == None:
                product = Product()
            else:
                product = Product.objects.get(id=product_id)
            product.user = request.user

            if product_id == None:
                product.product_name = dataForm.cleaned_data['product_name']
                product.slug = product.product_name.lower().replace(" ", "-")
            else:
                product.product_name = dataForm.cleaned_data['product_name'][1:]
                product.slug = product.product_name.lower().replace(" ", "-")

            if request.FILES:
                imageForm = MultipleImageUploadForm(request.POST, request.FILES)
                if imageForm.is_valid() == False: 
                    messages.error(request, "Lỗi khi tiếp nhận thông tin sản phẩm")
                    redirect('home')

                files = imageForm.cleaned_data['file_field']
                if product_id != None:
                    ImageSet.objects.get(set_id=product.images.set_id).delete()
                instance = ImageSet()
                instance.save() 
                product.images = instance

                for file in files:
                    image = ImageModel()
                    image.image = file
                    image.image_set = ImageSet.objects.get(set_id=product.images.set_id)
                    image.save()
                
            product.price = dataForm.cleaned_data['price']
            product.stock = dataForm.cleaned_data['stock']
            product.category = dataForm.cleaned_data['category']
            product.description = dataForm.cleaned_data['description']
            product.save()
            messages.success(request, "Sản phẩm đã được đăng tải !!!")
        else:
            messages.error(request, "Lỗi khi tiếp nhận thông tin sản phẩm")
        return redirect('home')

    if product_id != None:
        product = Product.objects.get(id=product_id)
        return render(request, 'accounts/uploadProducts.html', {'categories': categories, 'product': product, 'form': imageForm})
    return render(request, 'accounts/uploadProducts.html', {'categories': categories, 'form': imageForm})

def forgotPassword(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request=request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            send_email = EmailMessage(mail_subject, message, to=[email])
            send_email.send()

            messages.success(
                request=request, message="Email thay đổi mật khẩu đã được gửi")
    except Exception:
        messages.error(request=request, message="Tài khoản không tồn tại!")
    finally:
        context = {
            'email': email if 'email' in locals() else '',
        }
        return render(request, "accounts/forgotPassword.html", context=context)


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except Exception:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request=request, message='Hãy nhập mật khẩu mới')
        return redirect('reset_password')
    else:
        messages.error(request=request, message="Đường dẫn này đã hết hạn")
        return redirect('home')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, message="Thay đổi mật khẩu thành công")
            return redirect('login')
        else:
            messages.error(request, message="Mật khẩu không khớp")
    return render(request, 'accounts/reset_password.html')