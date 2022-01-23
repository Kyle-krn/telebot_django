from itertools import chain
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView
from bot.management.commands.utils import get_qiwi_balance
from django.db.models import Q
from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from django.utils.decorators import method_decorator
from online_shop.models import OrderSiteProduct, SoldSiteProduct
from online_shop.utils import send_email_change_status_order
from main_app.utils import change_item_order_utils, delete_order_utils, remove_item_order_utils
from .forms import *
from .models import *

def index(request):
    '''Функция для перенаправления юзеров'''
    if not request.user.is_authenticated:
        return redirect('login')
    return redirect('admin_panel:list_product') if request.user.is_superuser else redirect('local_shop:list_product')


@method_decorator(staff_member_required, name='dispatch')
class IndexView(LoginRequiredMixin, ListView):
    '''Вывод всех товаров'''
    context_object_name = 'product'
    template_name = 'main_app/list_product.html'

    def get_queryset(self):
        '''Фильтр по товарам'''
        queryset = Product.objects.all()
        if 'search' in self.request.GET:
            params = {k:v for k,v in self.request.GET.items() if len(v) != 0}
            if 'title' in params:
                queryset = queryset.filter(title__icontains=params['title'])
            if 'category' in params:
                queryset = queryset.filter(subcategory__category__pk=int(params['category']))
            if 'subcategory' in params:
                queryset = queryset.filter(subcategory__pk=int(params['subcategory']))
            if 'order_by' in params:
                queryset = queryset.order_by(params['order_by'])
        return queryset

    def post(self, request):
        '''Удаление товара'''
        form = ProductDeleteForm(request.POST)
        if form.is_valid():
            cf = form.cleaned_data
            Product.objects.get(pk=cf['id']).delete()
            return self.get(request)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.all()
        context['delete_form'] = ProductDeleteForm()
        return context


@method_decorator(staff_member_required, name='dispatch')
class CreateProductView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    '''Представление создания нового товара'''
    template_name = 'main_app/create_product.html'
    form_class = ProductForm
    success_message = "Товар успешно создан!"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.all()
        return context


@method_decorator(staff_member_required, name='dispatch')
class ReceptionProductView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    '''Представление добавления кол-ва товара (приемка)'''
    template_name = 'main_app/reception.html'
    form_class = ReceptionForm
    success_url = reverse_lazy('admin_panel:reception')
    success_message = 'Количество товара успешно увеличено!'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.all()
        return context


@method_decorator(staff_member_required, name='dispatch')
class CategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    '''Представление обновления категории/подкатегории'''
    model = Category
    template_name = 'main_app/category_detail.html'
    form_class = Category_reqForm
    success_url = reverse_lazy('admin_panel:create_category')
    success_message = 'Категория успешно обновлена!'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Изменить категорию/подкатегорию'
        return context

    def post(self, *args, **kwargs):
        if 'delete' in self.request.POST:   # Удаление категории/подкатегории
            category = self.get_object()
            category.delete()
            return redirect('admin_panel:create_category')
        return super().post(self)


@method_decorator(staff_member_required, name='dispatch')
class CategoriesView(LoginRequiredMixin, View):
    '''Представление создания/просмотра категорий/подкатегорий'''
    template_name = 'main_app/list_category.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['queryset'] = Category.objects.all()
        context['category_form'] = CategoryForm()
        context['sc_form'] = SubcategoryForm()
        return context

    def post(self, request):
        if 'create_category' in request.POST:   # Создать категорию
            category_form = CategoryForm(request.POST, files=request.FILES)
            if category_form.is_valid():
                category_form.save()
                messages.success(request, 'Новая категория успешно создана!')
                return redirect('admin_panel:create_category')

        elif 'create_sc' in request.POST:   # Создать подкатеогрию
            sc_form = SubcategoryForm(request.POST, files=request.FILES)
            if sc_form.is_valid():
                sc_form.save()
                messages.success(request, 'Новая подкатегория успешно создана!')
                return redirect('admin_panel:create_category')

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data())


@method_decorator(staff_member_required, name='dispatch')
class QiwiOrderView(LoginRequiredMixin, ListView):
    '''Представление просмотра заказов оплаченых через Qiwi'''
    template_name = 'main_app/order/paid_order.html'
    queryset = OrderingProduct.objects.filter(qiwi_bool=True).order_by('-datetime')
    context_object_name = 'queryset'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'QIWI заказы'
        return context


@method_decorator(staff_member_required, name='dispatch')
class NoPaidOrderView(LoginRequiredMixin, ListView):
    '''Представление неоплаченных заказы'''
    template_name = 'main_app/order/no_paid_order.html'
    queryset = OrderingProduct.objects.filter(Q(payment_bool=False) & Q(qiwi_bool=False)).order_by('-datetime')
    context_object_name = 'queryset'
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Неоплаченные заказы'
        return context

    def post(self, request):
        '''Отметить заказ оплаченным'''
        form = HiddenOrderIdForm(request.POST)
        if form.is_valid():
            cf = form.cleaned_data
            order = get_object_or_404(OrderingProduct, pk=cf['id'])
            for item in order.soldproduct.all():
                item.product.count -= item.count
                item.product.save()
                item.payment_bool = True
                item.save()
            order.payment_bool = True
            order.save()
            messages.success(request, 'Заказ успешно обработан!')
            return redirect('admin_panel:no_paid_order')


@method_decorator(staff_member_required, name='dispatch')
class PaidOrderView(LoginRequiredMixin, ListView):
    '''Представление просмотра оплаченных товаров'''
    template_name = 'main_app/order/paid_order.html'
    queryset = OrderingProduct.objects.filter(Q(payment_bool=True) & Q(qiwi_bool=False)).order_by('-datetime')
    context_object_name = 'queryset'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Оплаченные заказы'
        return context

############################################################################

@method_decorator(staff_member_required, name='dispatch')
class NoPaidSiteOrderView(LoginRequiredMixin, ListView):
    '''Неоплаченные заказы с сайта'''
    template_name = 'main_app/order/site_order.html'
    queryset = OrderSiteProduct.objects.filter(Q(status='Awaiting payment') & Q(pay_url__isnull=True)).order_by('-created')
    context_object_name = 'queryset'

    def post(self, request):
        '''Отметить заказ оплаченным'''
        form = HiddenOrderIdForm(request.POST)
        if form.is_valid():
            cf = form.cleaned_data
            order = get_object_or_404(OrderSiteProduct, pk=cf['id'])
            for item in order.soldproduct.all():
                item.product.count -= item.count
                item.product.save()
            order.status = 'Created'
            order.save()
            send_email_change_status_order(order.pk)
            messages.success(request, 'Заказ успешно обработан!')
            return redirect('admin_panel:site_no_paid_order')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Неоплаченные заказы с сайта'
        return context

@method_decorator(staff_member_required, name='dispatch')
class PaidSiteOrderView(LoginRequiredMixin, ListView):
    '''Оплаченные заказы с сайта'''
    template_name = 'main_app/order/paid_site_order.html'
    queryset = OrderSiteProduct.objects.exclude(status='Awaiting payment').filter(pay_url__isnull=True).order_by('-created')
    context_object_name = 'queryset'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Оплаченные заказы с сайта'
        return context

@method_decorator(staff_member_required, name='dispatch')
class QiwiSiteOrderView(LoginRequiredMixin, ListView):
    '''Киви заказы с сайта'''
    template_name = 'main_app/order/paid_site_order.html'
    queryset = OrderSiteProduct.objects.exclude(status='Awaiting payment').filter(pay_url__isnull=False).order_by('-created')
    context_object_name = 'queryset'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Qiwi заказы с сайта'
        return context

###############################################################################

@method_decorator(staff_member_required, name='dispatch')
class StatisticView(LoginRequiredMixin, View):
    '''Представления общей статистики по товарам'''
    template_name = 'main_app/statistic.html'
    
    def get_context_data(self, **kwargs):
        context = {}
        context['users'] = TelegramUser.objects.all().count()
        context['stat_dict'] = self.get_statistic()
        return context

    def get_statistic(self):
        '''Считает общую статистику, первый элемент кортежа - общая сумма денег, второй элемент - общее кол-во товара'''
        stat_dict = {'sold_stat' : (sum([x.count * x.price for x in self.bot_sold_queryset]) + sum([x.count * x.price for x in self.site_sold_queryset]), 
                                    sum([x.count for x in self.bot_sold_queryset]) + sum([x.count for x in self.site_sold_queryset])),
                 'reception_stat' : (sum([x.count * x.price for x in self.reception_queryset.filter(liquidated=False)]), sum([x.count for x in self.reception_queryset.filter(liquidated=False)])),
                 'liquidated_stat': (sum([x.count * x.price for x in self.reception_queryset.filter(liquidated=True)]) ,sum([x.count for x in self.reception_queryset.filter(liquidated=True)]))}
        stat_dict['all_stat'] = stat_dict['sold_stat'][0] - stat_dict['reception_stat'][0] - stat_dict['liquidated_stat'][0]
        return stat_dict

    def get_params(self):
        return {k:v for k,v in self.request.GET.items() if v != ''}

    def get_queryset(self):
        '''Фильтрует набор данных о приемке, продаже по заданной дате'''
        params = self.get_params()
        self.reception_queryset = ReceptionProduct.objects.all()
        self.bot_sold_queryset = SoldProduct.objects.filter(payment_bool=True)
        self.site_sold_queryset = SoldSiteProduct.objects.exclude(order__status='Awaiting payment')
        if 'start' in params and 'end' in params:
            self.bot_sold_queryset = self.bot_sold_queryset.filter(date__range=[params['start'], params['end']])
            self.site_sold_queryset = self.site_sold_queryset.filter(date__range=[params['start'], params['end']])
            self.reception_queryset = self.reception_queryset.filter(date__range=[params['start'], params['end']])
        elif 'start' in params:
            self.bot_sold_queryset = self.bot_sold_queryset.filter(date__gte=params['start'])
            self.site_sold_queryset = self.site_sold_queryset.filter(date__gte=params['start'])
            self.reception_queryset =self. reception_queryset.filter(date__gte=params['start'])
        elif 'end' in params:
            self.bot_sold_queryset = self.bot_sold_queryset.filter(date__lte=params['end'])
            self.site_sold_queryset = self.site_sold_queryset.filter(date__lte=params['end'])
            self.reception_queryset = self.reception_queryset.filter(date__lte=params['end'])      

    def get(self, request):
        self.get_queryset()
        return render(request, self.template_name, context=self.get_context_data())


@method_decorator(staff_member_required, name='dispatch')
class ProductView(LoginRequiredMixin, View):
    '''Детальное представление товара и управление им'''
    template_name = 'main_app/product_detail.html'
    
    def get_object(self):
        self.product = get_object_or_404(Product, pk=self.kwargs.get('pk'))

    def get_params(self):
        return {k:v for k,v in self.request.GET.items() if v != ''}

    def filter_queryset(self):
        '''Фильтрует набор данных для отображения таблицы (только приемка, только продажа, только ликвидированные товары или все)'''
        params = self.get_params()
        if 'only' in params:
            if params['only'] == 'reception':
                result_list = self.reception_queryset.filter(liquidated=False)
            elif params['only'] == 'sold':
                result_list = self.bot_sold_queryset
            elif params['only'] == 'liquidated':
                result_list = self.reception_queryset.filter(liquidated=True)
        else:
            result_list = sorted(
                    chain(self.reception_queryset, self.bot_sold_queryset, self.site_sold_queryset),
                    key=lambda instance: instance.date, reverse=True)
        return result_list

    def get_queryset(self, pk):
        '''Фильтрует набор данных о продажах и приемках по заданной дате'''
        params = self.get_params()
        self.reception_queryset = ReceptionProduct.objects.filter(product__pk=pk)
        self.bot_sold_queryset = SoldProduct.objects.filter(Q(product__pk=pk) & Q(payment_bool=True))
        self.site_sold_queryset = SoldSiteProduct.objects.exclude(order__status='Awaiting payment').filter(product__pk=pk)

        if 'start' in params and 'end' in params:
            self.bot_sold_queryset = self.bot_sold_queryset.filter(date__range=[params['start'], params['end']])
            self.site_sold_queryset = self.site_sold_queryset.filter(date__range=[params['start'], params['end']])
            self.reception_queryset = self.reception_queryset.filter(date__range=[params['start'], params['end']])
        elif 'start' in params:
            self.bot_sold_queryset = self.bot_sold_queryset.filter(date__gte=params['start'])
            self.site_sold_queryset = self.site_sold_queryset.filter(date__gte=params['start'])
            self.reception_queryset = self.reception_queryset.filter(date__gte=params['start'])
        elif 'end' in params:
            self.bot_sold_queryset = self.bot_sold_queryset.filter(date__lte=params['end'])
            self.site_sold_queryset = self.site_sold_queryset.filter(date__lte=params['end'])
            self.reception_queryset = self.reception_queryset.filter(date__lte=params['end'])   

    def get_statistic(self):
        '''Считает общую статистику, первый элемент кортежа - общая сумма денег, второй элемент - общее кол-во товара'''
        stat_dict = {
            'sold_stat': (sum([x.count * x.price for x in self.bot_sold_queryset]) + sum([x.count * x.price for x in self.site_sold_queryset]), 
                          sum([x.count for x in self.bot_sold_queryset]) + sum([x.count for x in self.site_sold_queryset])),
            'reception_stat': (sum([x.count * x.price for x in self.reception_queryset.filter(liquidated=False)]), sum([x.count for x in self.reception_queryset.filter(liquidated=False)])),
            'liquidated_stat': (sum([x.count * x.price for x in self.reception_queryset.filter(liquidated=True)]) ,sum([x.count for x in self.reception_queryset.filter(liquidated=True)]))
        }
        stat_dict['all_stat'] = stat_dict['sold_stat'][0] - stat_dict['reception_stat'][0]
        return stat_dict

    def get_context_data(self, **kwargs):
        context = {}
        context['product'] = self.product
        context['title'] = self.product.title
        context['category'] = Category.objects.all()
        context['reception_form'] = ReceptionForProductViewForm()
        context['stat_dict'] = self.get_statistic()
        context['trade_queryset'] = self.filter_queryset()
        context['product_form'] = Product_reqForm(initial={'title': self.product.title,
                                        'description': self.product.description,
                                        'price': self.product.price,
                                        'weight': self.product.weight,
                                        'subcategory': self.product.subcategory_id})
        context['reservation_count'] = self.check_reservation_product()
        return context

    def check_reservation_product(self):
        '''Вычисляет кол-во товара на бронировании'''
        product = self.product
        x = TelegramProductCartCounter.objects.filter(Q(product=product) & Q(counter=False))
        reservation_product = []
        for item in x:
            user = item.user
            if user.payproduct_set.all():
                reservation_product.append(item)
        reservation_count = sum([bp.count for bp in reservation_product])
        return reservation_count

    def post(self, request, pk):
        self.get_object()
        self.get_queryset(pk)

        if 'update' in request.POST:    # Обновить данные о товаре
            product_form = Product_reqForm(request.POST, files=request.FILES, instance=self.product)
            if product_form.is_valid():
                product_form.save()
                messages.success(request, 'Товар успешно обновлен!')
                return redirect('admin_panel:productdetail', pk=pk)

        elif 'delete' in request.POST:  # Удалить товар
            self.product.delete()
            messages.success(request, 'Товар усппешно удален!')
            return redirect ('admin_panel:list_product')

        elif 'reception' in request.POST:   # Приемка товара
            form = ReceptionForProductViewForm(request.POST)
            if form.is_valid():
                f = form.save(commit=False)
                f.product = self.product
                f.save()
                messages.success(request, 'Количество товара успешно увеличено!')
                return redirect('admin_panel:productdetail', pk=pk)   

        elif 'liquidated' in request.POST:  # Ликвидация товара
            form = ReceptionForProductViewForm(request.POST)
            if form.is_valid():
                f = form.save(commit=False)
                f.product = self.product
                f.liquidated = True
                f.save()
                messages.success(request, 'Товар успешно списан!')
                return redirect('admin_panel:productdetail', pk=pk)
        

    def get(self, request, pk):
        self.get_object()
        self.get_queryset(pk)
        return render(request, self.template_name, context=self.get_context_data())


class ControlQiwiView(LoginRequiredMixin, ListView):
    '''Представление контроля киви кошельков'''
    context_object_name = 'queryset'
    login_url = '/login/'
    template_name = 'main_app/control_qiwi.html'
    queryset = QiwiToken.objects.all()

    def post(self, request):
        if 'activate' in request.POST:          # Делает активный Qiwi кошелек для оплаты в боте
            form = QiwiIdForm(request.POST)
            if form.is_valid():
                cf = form.cleaned_data
                QiwiToken.objects.update(active=False)
                QiwiToken.objects.filter(pk=cf['id']).update(active=True)
        
        elif 'new_token' in request.POST:       # Добавляет новый Qiwi кошелек
            form = QiwiTokenForm(request.POST)
            try:
                balance = get_qiwi_balance(request.POST['number'], request.POST['token'])
                if form.is_valid():
                    qiwi = form.save()
                    qiwi.balance = balance
                    qiwi.save()
            except:
                messages.success(request, 'Ошибка получения баланса кошелька')

        elif 'del_tok' in request.POST:         # Удаляет qiwi кошелек
            form = QiwiIdForm(request.POST)
            if form.is_valid():
                cf = form.cleaned_data
                QiwiToken.objects.get(pk=cf['id']).delete()
        return redirect('admin_panel:control_qiwi')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = QiwiTokenForm()
        context['pay_product'] = PayProduct.objects.all()
        context['radio'] = QiwiIdForm()
        return context


@staff_member_required
def add_track_code_in_order(request, order_pk):
    '''Добавляет трек код к заказу'''
    instance = OrderingProduct.objects.get(pk=order_pk)
    form = TrackCodeForm(request.POST)
    if form.is_valid():
        cf = form.cleaned_data
        instance.track_code = cf['track_code']
        instance.save()
    return redirect('admin_panel:paid_order')


def add_track_code_and_status_order_site(request, order_pk):
    '''Добавлет трек и изменяет статус заказа'''
    instance = get_object_or_404(OrderSiteProduct, pk=order_pk)
    form = PaidOrderSiteForm(request.POST, instance=instance)
    if form.is_valid():
        form.save()
        send_email_change_status_order(instance.pk)
        return redirect('admin_panel:site_paid_order')


@staff_member_required
def change_item_bot_order(request, sold_pk):
    '''Изменяет кол-во проданного товара в неоплаченном заказе (заказ через мендежра в боте)'''
    instance = SoldProduct.objects.get(pk=sold_pk)
    change_item_order_utils(instance, request)
    return redirect('admin_panel:no_paid_order')


@staff_member_required
def change_item_site_order(request, sold_pk):
    '''Изменяет кол-во проданного товара в неоплаченном заказе (заказ через сайт)'''
    instance = SoldSiteProduct.objects.get(pk=sold_pk)
    change_item_order_utils(instance, request)
    return redirect('admin_panel:site_no_paid_order')


@staff_member_required
def delete_bot_order(request, order_pk):
    '''Полностью удаляет заказ (заказ через менеджера в боте)'''
    order = OrderingProduct.objects.get(pk=order_pk)
    delete_order_utils(order)
    return redirect('admin_panel:no_paid_order')


@staff_member_required
def delete_site_order(request, order_pk):
    '''Полностью удаляет заказ (заказ через сайт)'''
    order = OrderSiteProduct.objects.get(pk=order_pk)
    delete_order_utils(order)
    return redirect('admin_panel:site_new_order')


@staff_member_required
def remove_item_bot_order(request, sold_pk):
    '''Удаляет заданный товар из заказа (заказ через бота)'''
    instance = SoldProduct.objects.get(pk=sold_pk)
    remove_item_order_utils(instance)
    return redirect('admin_panel:no_paid_order')    


@staff_member_required
def remove_item_site_order(request, sold_pk):
    '''Удаляет заданный товар из заказа (заказ через сайт)'''
    instance = SoldSiteProduct.objects.get(pk=sold_pk)
    remove_item_order_utils(instance)
    return redirect('admin_panel:site_new_order')   








