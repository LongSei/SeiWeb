from orders.models import OrderProduct, Order
from django.contrib import messages
from store.forms import ReviewForm, StoreFilterForm
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.db.models import Q

from accounts.models import Account
from store.models import Product, ReviewRating, ImageSet
from carts.models import Cart, CartItem
from category.models import Category
from carts.views import _cart_id
from django.contrib.auth.decorators import login_required, permission_required

def store(request, category_slug=None):
    priceMin = 0
    priceMax = 1000000000
    if category_slug == None: 
        category_slug = 'all'
    if request.method == 'POST': 
        form = StoreFilterForm(request.POST)
        if form.is_valid():
            priceMin = int(request.POST['priceMin'])
            priceMax = int(request.POST['priceMax'])
            if 'category' in request.POST.keys(): 
                category_slug = str(request.POST['category'])
    if category_slug != 'all': 
        products = Product.objects.filter(price__gte=priceMin, price__lte=priceMax, category=Category.objects.get(slug=category_slug), is_available=True)    
    else:
        products = Product.objects.filter(price__gte=priceMin, price__lte=priceMax, is_available=True)    
    page = request.GET.get('page')
    page = page or 1
    paginator = Paginator(products, 3)
    paged_products = paginator.get_page(page)
    product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context=context)


def product_detail(request, category_slug, product_slug=None):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        cart = Cart.objects.get(cart_id=_cart_id(request=request))
        in_cart = CartItem.objects.filter(
            cart=cart,
            product=single_product
        ).exists()
    except Exception as e:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )

    product_ordered = OrderProduct.objects.filter(user__id=request.user.id, product__id=single_product.id)
    isBought = False
    for order in product_ordered: 
        isBought |= (order.order.status == "Hoàn thành")
    
    isBought |= (request.user.is_anonymous == False and request.user.is_superadmin == True)

    reviews = ReviewRating.objects.filter(product_id=single_product.id)

    user_review = None
    if ReviewRating.objects.filter(user__id=request.user.id).exists():
        user_review = ReviewRating.objects.get(user__id=request.user.id)
        
    context = {
        'single_product': single_product,
        'in_cart': in_cart if 'in_cart' in locals() else False,
        'user_review': user_review,
        'isBought': isBought,
        'reviews': reviews,
    }
    return render(request, 'store/product_detail.html', context=context)


def search(request):
    if 'q' in request.GET:
        q = request.GET.get('q')
        products = Product.objects.order_by('-created_date').filter(Q(product_name__icontains=q) | Q(description__icontains=q))
        product_count = products.count()
    context = {
        'products': products,
        'q': q,
        'product_count': product_count
    }
    return render(request, 'store/store.html', context=context)

@login_required(login_url='login')
def delete_review(request, product_id): 
    url = request.META.get('HTTP_REFERER')
    try:
        ReviewRating.objects.get(user__id=request.user.id, product__id=product_id).delete() 
        messages.success(request, "Đã xoá đánh giá thành công !") 
        return redirect(url)
    except: 
        messages.error(request, "Không thể xoá đánh giá !") 
        return redirect(url)

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    product_ordered = OrderProduct.objects.filter(user__id=request.user.id, product__id=product_id)
    isBought = False
    for order in product_ordered: 
        isBought |= (order.order.status == "Hoàn thành")
    if request.method == "POST":
        if isBought != True and request.user.is_anonymous == False and request.user.is_superadmin == False: 
            messages.error(request, "Bạn cần mua sản phẩm trước khi có thể đánh giá")
            return redirect(url)
        else: 
            isExist = ReviewRating.objects.filter(user__id=request.user.id, product__id=product_id).exists()
            if isExist == True:
                review = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
                form = ReviewForm(request.POST, instance=review)
                form.save()
                messages.success(request, "Đánh giá của bạn đã được cập nhật")
                return redirect(url)
            else:
                form = ReviewForm(request.POST)
                if form.is_valid():
                    data = ReviewRating()
                    data.subject = form.cleaned_data['subject']
                    data.rating = form.cleaned_data['rating']
                    data.review = form.cleaned_data['review']
                    data.product =Product.objects.get(id=product_id)
                    instance = ImageSet()
                    instance.save()
                    data.images = instance
                    data.user = Account.objects.get(id=request.user.id)
                    data.save()
                    messages.success(request, "Đánh giá của bạn đã được ghi nhận")
                    return redirect(url)
