from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from django.views import View
from main_app.models import Product
from .forms import *

class CartDetailView(View):
    '''Детальное представление корзины'''
    template_name = 'cart/cart_detail.html'
    
    def get_user_cart(self):
        '''Получение корзины юзера'''
        cart = get_cart(self.request)
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
        return (temp_cart.values(), cart_total_price)

    def get_context_data(self, **kwargs):
        context = {}
        cart = self.get_user_cart()
        context['cart'] = cart[0]
        context['profile_form'] = cart[1]
        return context

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data())


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
    return redirect('cart:cart_detail')


def cart_remove(request, product_id):
    '''Удаление товара из корзины'''
    cart = get_cart(request)
    product_id = str(product_id)
    if product_id in cart:
        del cart[product_id]
        request.session.modified = True
        return redirect('cart:cart_detail')


def cart_clean(request):
    '''Отчистить корзину'''
    del request.session[settings.CART_ID]
