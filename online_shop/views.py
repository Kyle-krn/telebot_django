from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import *
from main_app.models import Category, SubCategory, Product, SoldProduct, SoldSiteProduct
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
    cart = get_cart(request)
    print(cart)
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)
    temp_cart = cart.copy()

    for product in products:

        # if product.count <= 0:
        #     # cart_remove(request, product.pk)
        #     # request.session.modified = True
        #     del temp_cart[str(product.pk)]
        #     continue

        cart_item = temp_cart[str(product.pk)]

        if cart_item['quantity'] > product.count:
            cart_item['quantity'] = product.count


        cart_item['product'] = product
        cart_item['total_price'] = (Decimal(cart_item['price']) * cart_item['quantity'])
        cart_item['update_quantity_form'] = CartAddProductForm(initial={'quantity': cart_item['quantity']})

        # if product.count <= 0:
        #     cart_remove(request, product.pk)
            # request.session.modified = True
            # del temp_cart[str(product.pk)]
            # continue


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


def order_create(request):
    cart = get_cart(request)
    weight = sum([x['weight'] * x['quantity'] for x in cart.values()])
    # delivery = check_price_delivery(request.GET['id_postal_code'], weight)

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
            cart_clean(request)
            # # order_created.delay(order.pk)
            return render( request, 'order_created.html', {'order': order})

            return redirect('online_shop:cart_detail')
        else:
            return render(request,'product/order_create.html', {'cart': cart, 'order_form': order_form})
    else:
        order_form = OrderCreateForm()
        return render(request,'product/order_create.html', {'cart': cart, 'order_form': order_form})


from django.http import JsonResponse
from main_app.management.commands.utils import check_price_delivery
def validate_username(request):
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