from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import *
from main_app.models import Category, SubCategory, Product
from decimal import Decimal
from django.conf import settings


def product_list(request, subcategory_slug=None):
    categories = Category.objects.all()
    if subcategory_slug:
        requested_category = get_object_or_404(SubCategory, slug=subcategory_slug)
        products = Product.objects.filter(subcategory=requested_category)
    else:
        requested_category = None
        products = Product.objects.all()
    return render(request, 'product/list.html', {'categories': categories, 'requested_category': requested_category, 'products': products})


def product_detail(request, subcategory_slug, product_slug):
    # category = get_object_or_404(Category, slug=category_slug)
    product = get_object_or_404(Product, slug=product_slug)
    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            cf = review_form.cleaned_data
            author_name = 'Annonymous'
            Review.objects.create(product=product, author=author_name, rating=cf['rating'], text=cf['text'])
            return redirect('online_shop:product_detail', subcategory_slug=subcategory_slug, product_slug=product_slug)
    else:
        review_form = ReviewForm()
        cart_product_form = CartAddProductForm()
    return render(request, 'product/detail.html', {'product': product, 'review_form': review_form, 'cart_product_form': cart_product_form})
# Create your views here.

def get_cart(request):
    cart = request.session.get(settings.CART_ID)
    if not cart:
        cart = request.session[settings.CART_ID] = {}
    return cart

def cart_add(request, product_id):
    cart = get_cart(request)
    product = get_object_or_404(Product, pk=product_id)
    product_id = str(product.id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data

        if product_id not in cart:
            cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if request.POST.get('overwrite_qty'):
            cart[product_id]['quantity'] = cd['quantity']
        else:
            cart[product_id]['quantity'] += cd['quantity']
        request.session.modified = True
    return redirect('online_shop:cart_detail')


def cart_detail(request):
    cart = get_cart(request)
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)
    temp_cart = cart.copy()

    for product in products:
        cart_item = temp_cart[str(product.pk)]
        cart_item['product'] = product
        cart_item['total_price'] = (Decimal(cart_item['price']) * cart_item['quantity'])
        cart_item['update_quantity_form'] = CartAddProductForm(initial={'quantity': cart_item['quantity']})

    cart_total_price = sum(Decimal(item['price']) * item['quantity'] for item in temp_cart.values())
    return render(request, 'product/cart_detail.html', {'cart': temp_cart.values(), 'cart_total_price': cart_total_price})


def cart_remove(request, product_id):
    cart = get_cart(request)
    product_id = str(product_id)
    if product_id in cart:
        del cart[product_id]

        request.session.modified = True
        return redirect('online_shop:cart_detail')


def cart_clean(request):
    del request.session[settings.CART_ID]