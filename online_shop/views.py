from django.shortcuts import render, get_object_or_404, redirect
import requests
from .models import *
from .forms import *
from main_app.models import Category, SubCategory, Product, SoldProduct
from .models import *
from decimal import Decimal
from django.conf import settings
from main_app.tasks import order_created
from .utils import send_email_created_order
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from main_app.utils import check_price_delivery

def product_list(request, category_slug=None, subcategory_slug=None):
    '''Представление каталога товаров'''
    categories = Category.objects.all()
    if category_slug and subcategory_slug:
        requested_subcategory = get_object_or_404(SubCategory, slug=subcategory_slug)
        requested_category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(subcategory=requested_subcategory)
    elif category_slug:
        requested_subcategory = None
        requested_category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(subcategory__category=requested_category)
    else:
        requested_category = None
        requested_subcategory = None
        products = Product.objects.all()
    return render(request, 'product/list.html', {'categories': categories, 'requested_subcategory': requested_subcategory, 'requested_category': requested_category, 'products': products})


def product_detail(request, product_slug):
    '''Детальное представление товара'''
    product = get_object_or_404(Product, slug=product_slug)
    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            cf = review_form.cleaned_data
            author_name = 'Annonymous'
            if request.user.is_authenticated and request.user.first_name != '':
                author_name = request.user.first_name

            Review.objects.create(product=product, author=author_name, rating=cf['rating'], text=cf['text'])
            return redirect('online_shop:product_detail', product_slug=product_slug)
    else:
        review_form = ReviewForm()
        cart_product_form = CartAddProductForm()
    return render(request, 'product/detail.html', {'product': product, 'review_form': review_form, 'cart_product_form': cart_product_form})


def get_cart(request):
    '''Получить корзину'''
    cart = request.session.get(settings.CART_ID)
    if not cart:
        cart = request.session[settings.CART_ID] = {}
    return cart


def cart_add(request, product_id):
    '''Добавление товара в корзину'''
    cart = get_cart(request)
    product = get_object_or_404(Product, pk=product_id)
    product_id = str(product.id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data

        if cd['quantity'] > product.count:
            cd['quantity'] = product.count

        if product_id not in cart:
            cart[product_id] = {'quantity': 0, 'price': str(product.price), 'weight': product.weight}
        if request.POST.get('overwrite_qty'):
            cart[product_id]['quantity'] = cd['quantity']
        else:
            if (cd['quantity'] + cart[product_id]['quantity']) > product.count:
                cart[product_id]['quantity'] = product.count
            else:
                cart[product_id]['quantity'] += cd['quantity']
        request.session.modified = True
    return redirect('online_shop:cart_detail')


def cart_detail(request):
    '''Детальное представление корзины'''
    cart = get_cart(request)
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)
    temp_cart = cart.copy()

    for product in products:

        cart_item = temp_cart[str(product.pk)]

        if cart_item['quantity'] > product.count:
            cart_item['quantity'] = product.count


        cart_item['product'] = product
        cart_item['total_price'] = (Decimal(cart_item['price']) * cart_item['quantity'])
        cart_item['update_quantity_form'] = CartAddProductForm(initial={'quantity': cart_item['quantity']})


    cart_total_price = sum(Decimal(item['price']) * item['quantity'] for item in temp_cart.values())
    return render(request, 'product/cart_detail.html', {'cart': temp_cart.values(), 'cart_total_price': cart_total_price})


def cart_remove(request, product_id):
    '''Удаление товара из корзины'''
    cart = get_cart(request)
    product_id = str(product_id)
    if product_id in cart:
        del cart[product_id]

        request.session.modified = True
        return redirect('online_shop:cart_detail')


def cart_clean(request):
    '''Отчистить корзину'''
    del request.session[settings.CART_ID]

from django.core.mail import send_mail

def order_create(request):
    '''Представление создания заказа'''
    cart = get_cart(request)
    weight = sum([x['weight'] * x['quantity'] for x in cart.values()])

    if request.method == 'POST':
        order_form = OrderCreateForm(request.POST)
        if order_form.is_valid():
            cf = order_form.cleaned_data
            delivery_price = check_price_delivery(cf['postal_code'], weight)
            order = order_form.save(commit=False)
            order.transport_cost = delivery_price
            order.save()
            product_ids = cart.keys()
            products = Product.objects.filter(id__in=product_ids)
            for product in products:
                cart_item =cart[str(product.id)]
                SoldSiteProduct.objects.create(product=product, price=product.price, count=cart_item['quantity'], order=order)
            order.set_order_price()
            cart_clean(request)
            send_email_created_order(order.pk)
            return render( request, 'product/order_created.html', {'order': order})
        else:
            return render(request,'product/order_create.html', {'cart': cart, 'order_form': order_form})
    else:
        order_form = OrderCreateForm()
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            }
        return render(request,'product/order_create.html', {'cart': cart, 'order_form': order_form})


def validate_postal_code(request):
    """Валидация почтового идекса для AJAX"""
    postal_code = request.GET['id_postal_code']
    if len(postal_code) != 6:
        return JsonResponse({'error': 'error'}, status=403)
    try:
        cart = get_cart(request)
        weight = sum([x['weight'] * x['quantity'] for x in cart.values()])
        delivery = check_price_delivery(request.GET['id_postal_code'], weight)
        response = JsonResponse({'is_taken': delivery}, status=200)
    except:
        response = JsonResponse({'error': 'error'}, status=403)
    return response


