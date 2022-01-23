from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import weasyprint
from cart.forms import CartAddProductForm
from cart.views import cart_clean, get_cart
from main_app.utils import check_price_delivery
from main_app.models import Category, SubCategory, Product
from bot.management.commands.handlers.handlers import bot
from .utils import send_email_order_method_payment_qiwi, send_email_order_method_payment_manager, create_bill_qiwi
from .models import *
from .models import *
from .forms import *


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
            self.requested_subcategory = get_object_or_404(
                SubCategory, slug=self.subcategory_slug)
            self.requested_category = get_object_or_404(
                Category, slug=self.category_slug)
            queryset = Product.objects.filter(
                subcategory=self.requested_subcategory)
        elif self.category_slug:
            '''Товары категории'''
            self.requested_subcategory = None
            self.requested_category = get_object_or_404(
                Category, slug=self.category_slug)
            queryset = Product.objects.filter(
                subcategory__category=self.requested_category)
        else:
            '''Все товары'''
            self.requested_category = None
            self.requested_subcategory = None
            queryset = Product.objects.all()
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        # Активна категория
        context['requested_category'] = self.requested_category
        # Активная подкатегория
        context['requested_subcategory'] = self.requested_subcategory
        return context


class ProductDetailView(DetailView):
    '''Страница товара'''
    model = Product
    context_object_name = 'product'
    template_name = 'product/detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_form'] = ReviewForm()       # Форма отзывов
        # Форма добавления в корзину
        context['cart_product_form'] = CartAddProductForm()
        return context

    def post(self, request, slug):
        '''Добавление отзыва к товару'''
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            cf = review_form.cleaned_data
            author_name = 'Annonymous'
            if request.user.is_authenticated and request.user.first_name != '':
                author_name = request.user.first_name
            Review.objects.create(product=self.get_object(
            ), author=author_name, rating=cf['rating'], text=cf['text'])
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
        delivery_price = check_price_delivery(
            cf['postal_code'], weight)        # Стоимость доставки почтой РФ
        order = form.save(commit=False)
        if self.request.user.is_authenticated:
            order.user = self.request.user
        order.transport_cost = delivery_price
        order.save()
        product_ids = cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            '''Добавляем товары из корзины в заказ'''
            cart_item = cart[str(product.id)]
            SoldSiteProduct.objects.create(
                product=product, price=product.price, count=cart_item['quantity'], order=order)
        order.set_order_price()     # Устанавливаем цену заказа
        cart_clean(self.request)    # Чистим корзину
        if 'manager_payment' in self.request.POST:
            '''Оплата через менедежра'''
            send_email_order_method_payment_manager(order.pk)
            text_for_channel = '<b>Заказ через сайт</b>\n'  \
                               '<b>Оплата через менеджера</b>\n\n'  \
                               f'<b>Сумма корзины {order.price} руб.</b>\n\n'  \
                               f'<b>Сумма доставки {order.transport_cost} руб.</b>\n\n'
            for item in order.soldproduct.all():
                text_for_channel += f'<b><u>{item.product.title}</u></b> - {item.count} шт.\n'
            text_for_channel += f'\n<b>Номер телефона покупателя - {cf["telephone"]}</b>'
            bot.send_message(chat_id=settings.TELEGRAM_GROUP_ID, text=text_for_channel,
                             disable_web_page_preview=True, parse_mode='HTML')
            return render(self.request, 'product/order_created.html', {'order': order})
        else:
            '''Оплата через QIWI'''
            bill = create_bill_qiwi(order.pk)
            order.pay_url = bill
            order.save()
            send_email_order_method_payment_qiwi(order.pk)
            return render(self.request, 'product/order_qiwi_created.html', {'order': order})

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
        # Возвращаем стоймость доставки
        response = JsonResponse({'is_taken': delivery}, status=200)
    except KeyError:
        '''Невалидный индекс'''
        response = JsonResponse({'error': 'error'}, status=403)
    return response



def invoice_pdf(request, order_id):
    order = get_object_or_404(OrderSiteProduct, id=order_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    # generate pdf
    html = render_to_string('pdf.html', {'order': order})
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=stylesheets)
    return response
