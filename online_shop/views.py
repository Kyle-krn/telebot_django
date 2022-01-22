from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.shortcuts import render, get_object_or_404, redirect
from cart.forms import CartAddProductForm
from cart.views import cart_clean, get_cart
from .models import *
from .forms import *
from main_app.models import Category, SubCategory, Product
from .models import *
from .utils import send_email_order_method_payment_qiwi, send_email_order_method_payment_manager, create_bill_qiwi
from django.http import JsonResponse
from main_app.utils import check_price_delivery


class ProductListView(ListView):
    '''Каталог товаров'''
    context_object_name = 'products'
    template_name = 'product/list.html'

    def get_queryset(self):
        queryset = Product.objects.all() 
        self.category_slug = self.kwargs.get('category_slug')
        self.subcategory_slug = self.kwargs.get('subcategory_slug')
        if self.category_slug and self.subcategory_slug:
            '''Товары подкатегории'''
            self.requested_subcategory = get_object_or_404(SubCategory, slug=self.subcategory_slug)
            self.requested_category = get_object_or_404(Category, slug=self.category_slug)
            queryset = Product.objects.filter(subcategory=self.requested_subcategory)
        elif self.category_slug:
            '''Товары категории'''
            self.requested_subcategory = None
            self.requested_category = get_object_or_404(Category, slug=self.category_slug)
            queryset = Product.objects.filter(subcategory__category=self.requested_category)
        else:
            '''Все товары'''
            self.requested_category = None
            self.requested_subcategory = None
            queryset = Product.objects.all()
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['requested_category'] = self.requested_category     # Активна категория
        context['requested_subcategory'] = self.requested_subcategory   # Активная подкатегория
        return context


class ProductDetailView(DetailView):
    '''Страница товара'''
    model = Product
    context_object_name = 'product'
    template_name = 'product/detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_form'] = ReviewForm()       # Форма отзывов
        context['cart_product_form'] = CartAddProductForm()     # Форма добавления в корзину
        return context

    def post(self, request, slug):
        '''Добавление отзыва к товару'''
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            cf = review_form.cleaned_data
            author_name = 'Annonymous'
            if request.user.is_authenticated and request.user.first_name != '':
                author_name = request.user.first_name
            Review.objects.create(product=self.get_object(), author=author_name, rating=cf['rating'], text=cf['text'])
            return redirect('online_shop:product_detail', slug=slug)


class CreateOrderView(CreateView):
    '''Оформление заказа'''
    template_name = 'product/order_create.html'
    form_class = OrderCreateForm

    def get_initial(self):
        '''Если это зарегистрированный пользователь, заполняем форму его данными'''
        super(CreateOrderView, self).get_initial()
        if self.request.user.is_authenticated:
            self.initial = {
                'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
                'email': self.request.user.email,
                'telephone': self.request.user.profile.phone_number,
                'address': self.request.user.profile.address,
                'postal_code': self.request.user.profile.postal_code,
                'city': self.request.user.profile.city,
            }
        return self.initial

    def form_valid(self, form):
        '''Оформление заказа'''
        cart = get_cart(self.request)
        weight = sum([x['weight'] * x['quantity'] for x in cart.values()])
        cf = form.cleaned_data
        delivery_price = check_price_delivery(cf['postal_code'], weight)        # Стоимость доставки почтой РФ
        order = form.save(commit=False)
        if self.request.user.is_authenticated:
                order.user = self.request.user
        order.transport_cost = delivery_price
        # order.transport_cost = 1
        order.save()
        product_ids = cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            '''Добавляем товары из корзины в заказ'''
            cart_item =cart[str(product.id)]
            SoldSiteProduct.objects.create(product=product, price=product.price, count=cart_item['quantity'], order=order)
        order.set_order_price()     # Устанавливаем цену заказа
        cart_clean(self.request)    # Чистим корзину
        if 'manager_payment' in self.request.POST:
            '''Оплата через менедежра'''
            send_email_order_method_payment_manager(order.pk)
            return render( self.request, 'product/order_created.html', {'order': order})
        else:
            '''Оплата через QIWI'''
            bill = create_bill_qiwi(order.pk)
            order.pay_url = bill
            order.save()
            send_email_order_method_payment_qiwi(order.pk)
            return render( self.request, 'product/order_qiwi_created.html', {'order': order})


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = get_cart(self.request)
        return context


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
    except KeyError:
        '''Невалидный индекс'''
        response = JsonResponse({'error': 'error'}, status=403)
    return response


