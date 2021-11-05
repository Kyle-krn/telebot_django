from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .models import *
from django.contrib import messages
from .forms import *
from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import ListView
from itertools import chain
from collections import Counter
from datetime import date
from django.db.models import Q, F, Sum
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from main_app.management.commands.handlers.handlers import bot
from vape_shop.settings import TELEGRAM_GROUP_ID
from django.contrib.auth.models import Group, User


class CreateOrderView(LoginRequiredMixin, View):
    template_name = 'seller_site/create_order.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['title'] = 'Создать чек'
        context['category'] = OfflineCategory.objects.all()
        return context

    def post(self, request):
        if 'product_id' not in request.POST and 'product_count' not in request.POST:
            messages.error(request, 'Ошибка добавления чека!')
            return redirect('local_shop:list_product')

        pk_list = request.POST.getlist('product_id')    
        count_list = request.POST.getlist('product_count')

        if len(pk_list) != len(count_list):     # Доп проверка
            messages.error(request, 'Ошибка добавления чека!')
            return redirect('local_shop:list_product')

        try:
            l_list = [(int(pk_list[i]), int(count_list[i])) for i in range(len(pk_list))]
        except (ValueError, TypeError):
            messages.error(request, 'Ошибка добавления чека!')
            return redirect('local_shop:list_product')

        c = Counter()
        for item in l_list:         # Прогоняем через Counter что бы не плодить одинаковые товары в чеке
            c[item[0]] += item[1]
        l_list = c.most_common()        
        order = OfflineOrderingProduct.objects.create(user=request.user)    # Создаем чек
        total_price = 0
        for item in l_list: # Добавляем проданные товары в чек
            product = get_object_or_404(OfflineProduct, pk=item[0])
            OfflineSoldProduct.objects.create(user=request.user, product=product,title=product.title ,price=product.price, count=item[1], price_for_seller=product.subcategory.category.price_for_seller, order=order)
            total_price += product.price * item[1]
        order.price = total_price
        order.save()
        bot.send_message(chat_id=TELEGRAM_GROUP_ID, text=f'Новый чек на сумму {order.price} руб. Продавец - {request.user.first_name} {request.user.last_name}')
        messages.success(request, 'Чек успешно создан!')
        return redirect('local_shop:list_product')   

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data())



class OfflineReceptionProductView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    '''Представление добавления кол-ва товара (приемка)'''
    template_name = 'seller_site/create_reception.html'
    form_class = OfflineReceptionForm
    success_url = reverse_lazy('local_shop:create_reception')
    success_message = 'Количество товара успешно увеличено!'

    def form_valid(self, form):
        product = get_object_or_404(OfflineProduct, pk=int(self.request.POST['product']))
        f = form.save(commit=False)
        f.price = product.purchase_price
        f.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Приемка товара'
        context['category'] = OfflineCategory.objects.all()
        return context

@method_decorator(staff_member_required, name='dispatch')
class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'seller_site/register.html'
    success_url = reverse_lazy('local_shop:list_product')

    def form_valid(self, form, *args, **kwargs):
        self.object = form.save()
        seller_group = Group.objects.get_or_create(name='sellers')
        seller_group[0].user_set.add(self.object)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация продовца'
        return context


@method_decorator(staff_member_required, name='dispatch')
class OfflineCategoriesView(LoginRequiredMixin, View):
    '''Представление создания/просмотра категорий/подкатегорий'''
    template_name = 'seller_site/list_category.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['title'] = 'Категории (Оффлайн магазин)'
        context['category'] = OfflineCategory.objects.all()
        context['category_form'] = OffilneCategoryForm()

        context['change_category_form'] = OffilneChangeCategoryForm(auto_id="change_category_%s")
        context['change_subcategory_form'] = OfflineChangeSubcategoryForm(auto_id="change_subcategory_%s")

        context['sc_form'] = OfflineSubcategoryForm()
        return context

    def post(self, request):
        if 'create_category' in request.POST:   # Создать категорию
            category_form = OffilneCategoryForm(request.POST)
            if category_form.is_valid():
                category_form.save()
                messages.success(request, 'Новая категория успешно создана!')
                

        elif 'change_category' in request.POST: # Изменить категорию
            try:
                instance = get_object_or_404(OfflineCategory, pk=int(request.POST.get('id')))
            except (ValueError, TypeError):
                messages.error(request, 'Ошибка изменения категории')

            category_form = OffilneChangeCategoryForm(request.POST, instance=instance)
            if category_form.is_valid():
                category_form.save()
                messages.success(request, 'Категория успешно обновлена!')


        elif 'delete_category' in request.POST:     # Удалить категорию
            if 'category_pk' not in request.POST:
                messages.error(request, 'Ошибка удаления категории!')
                return redirect('local_shop:list_product')
            try:
                category_pk = int(request.POST.get('category_pk'))
            except (ValueError, TypeError):
                messages.error(request, 'Ошибка удаления категории!')
                return redirect('local_shop:list_product')

            get_object_or_404(OfflineCategory, pk=category_pk).delete()
            messages.success(request, 'Категория успешно удалена!')

        elif 'create_sc' in request.POST:   # Создать подкатеогрию
            sc_form = OfflineSubcategoryForm(request.POST)
            if sc_form.is_valid():
                sc_form.save()
                messages.success(request, 'Новая подкатегория успешно создана!')

        elif 'change_subcategory' in request.POST:

            try:
                instance = get_object_or_404(OfflineSubCategory, pk=int(request.POST.get('id')))
            except (ValueError, TypeError):
                messages.error(request, 'Ошибка изменения категории')

            subcategory_form = OfflineChangeSubcategoryForm(request.POST, instance=instance)
            if subcategory_form.is_valid():
                subcategory_form.save()
                messages.success(request, 'Подкатегория успешно обновлена!')


        elif 'delete_subcategory' in request.POST:      # Удалить подкатегорию
            if 'subcategory_pk' not in request.POST:
                messages.error(request, 'Ошибка удаления подкатегории!')
                return redirect('local_shop:list_product')
            
            try:
                subcategory_pk = int(request.POST.get('subcategory_pk'))
            except (ValueError, TypeError):
                messages.error(request, 'Ошибка удаления подкатегории!')
                return redirect('local_shop:list_product')

            get_object_or_404(OfflineSubCategory, pk=subcategory_pk).delete()
            messages.success(request, 'Подкатегория успешно удалена!')
        return redirect('local_shop:list_category')

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data())


@method_decorator(staff_member_required, name='dispatch')
class OfflineCreateProductView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    '''Создание нового товара'''
    template_name = 'seller_site/create_product.html'
    form_class = OfflineProductForm
    success_message = "Товар успешно создан!"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Новый товар'
        context['category'] = OfflineCategory.objects.all()
        return context


class OfflineIndexView(LoginRequiredMixin, ListView):
    '''Вывод всех товаров'''
    context_object_name = 'product'
    login_url = '/login/'
    template_name = 'seller_site/list_product.html'

    @method_decorator(staff_member_required, name='dispatch')
    def post(self, request):
        if 'delete_product' in request.POST:
            if 'pk_p' not in request.POST:
                messages.error(request, 'Ошибка удаления товара!')
                return redirect('local_shop:list_product')

            try:
                pk_product = int(request.POST.get('pk_p'))
            except (ValueError, TypeError):
                messages.error(request, 'Ошибка удаления товара!')
                return redirect('local_shop:list_product')

            get_object_or_404(OfflineProduct, pk=pk_product).delete()
            return redirect('local_shop:list_product')

    def get_queryset(self):
        queryset = OfflineProduct.objects.all()
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

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Все товары'
        context['category'] = OfflineCategory.objects.all()
        return context


@method_decorator(staff_member_required, name='dispatch')
class OfflineProductAdminView(LoginRequiredMixin, View):
    '''Детальное представление товара и управление им'''
    template_name = 'seller_site/product_detail.html'
    
    def get_object(self):
        self.product = get_object_or_404(OfflineProduct, pk=self.kwargs.get('pk'))

    def get_params(self):
        return {k:v for k,v in self.request.GET.items() if v != ''}

    def get_context_data(self, **kwargs):
        context = {}
        context['product'] = self.product
        context['title'] = self.product.title
        context['category'] = OfflineCategory.objects.all()
        context['reception_form'] = OfflineReceptionForProductViewForm()
        context['stat_dict'] = self.get_statistic()
        context['trade_queryset'] = self.filter_queryset()
        context['product_form'] = OfflineProductForm(initial={'title': self.product.title,
                                        'price': self.product.price,
                                        'purchase_price': self.product.purchase_price,
                                        'subcategory': self.product.subcategory_id})
        return context

    def filter_queryset(self):
        '''Сортирует result_list для таблицы (будет выводиться: Только проданные, только закупленные, только списанные или все)'''
        params = self.get_params()
        if 'only' in params:
            if params['only'] == 'reception':
                result_list = self.reception_queryset.filter(liquidated=False)
            elif params['only'] == 'sold':
                result_list = self.sold_queryset
            else:
                result_list = self.reception_queryset.filter(liquidated=True)
        else:
            result_list = sorted(
                    chain(self.reception_queryset, self.sold_queryset),
                    key=lambda instance: instance.date, reverse=True)
        return result_list

    def get_queryset(self, pk):
        '''Берет queryset по дате'''
        params = self.get_params()
        self.reception_queryset = OfflineReceptionProduct.objects.filter(product__pk=pk)
        self.sold_queryset = OfflineSoldProduct.objects.filter(product__pk=pk)

        if 'start' in params and 'end' in params:
            self.sold_queryset = self.sold_queryset.filter(date__range=[params['start'], params['end']])
            self.reception_queryset = self.reception_queryset.filter(date__range=[params['start'], params['end']])
        elif 'start' in params:
            self.sold_queryset = self.sold_queryset.filter(date__gte=params['start'])
            self.reception_queryset = self.reception_queryset.filter(date__gte=params['start'])
        elif 'end' in params:
            self.sold_queryset = self.sold_queryset.filter(date__lte=params['end'])
            self.reception_queryset = self.reception_queryset.filter(date__lte=params['end']) 

    def get_statistic(self):
        '''Статистика по товару'''
        stat_dict = {
            'sold_stat': [int(x or 0) for x in tuple(self.sold_queryset.annotate(sold_sum=F('count') * F('price')).aggregate(all_sold_price = Sum('sold_sum'),all_sold_count = Sum('count')).values())],
            'reception_stat': [int(x or 0) for x in tuple(self.reception_queryset.filter(liquidated=False).annotate(reception_sum=F('count') * F('price')).aggregate(all_reception_price= Sum('reception_sum'), all_reception_count=Sum('count')).values())],
            'liquidated_stat':[int(x or 0) for x in tuple(self.reception_queryset.filter(liquidated=True).annotate(reception_sum=F('count') * F('price')).aggregate(all_reception_price= Sum('reception_sum'), all_reception_count=Sum('count')).values())]
        }
        stat_dict['all_stat'] = stat_dict['sold_stat'][0] - stat_dict['reception_stat'][0]
        return stat_dict

    def post(self, request, pk):
        self.get_object()
        if 'update' in request.POST:    # Изменить товар
            product_form = OfflineProductForm(request.POST, instance=self.product)
            if product_form.is_valid():
                product_form.save()
                messages.success(request, 'Товар успешно обновлен!')
                return redirect('local_shop:product_detail', pk=pk)

        elif 'delete' in request.POST:  # Удалить товар
            self.product.delete()
            messages.success(request, 'Товар усппешно удален!')
            return redirect ('local_shop:list_product')

        elif 'reception' in request.POST:   # Приемка товара
            form = OfflineReceptionForProductViewForm(request.POST)
            if form.is_valid():
                f = form.save(commit=False)
                f.product = self.product
                f.price = self.product.purchase_price
                f.user = request.user
                f.save()
                messages.success(request, 'Количество товара успешно увеличено!')
                return redirect('local_shop:product_detail', pk=pk)

        elif 'liquidated' in request.POST:  # Ликвидация товара
            form = OfflineReceptionForProductViewForm(request.POST)
            if form.is_valid():
                f = form.save(commit=False)
                f.product = self.product
                f.price = self.product.purchase_price
                f.user = request.user
                f.liquidated = True
                f.save()
                messages.success(request, 'Товар успешно списан!')
                return redirect('local_shop:product_detail', pk=pk)
 
    def get(self, request, pk):
        self.get_object()
        self.get_queryset(pk)
        return render(request, self.template_name, context=self.get_context_data())


@method_decorator(staff_member_required, name='dispatch')
class OfflineOrderView(LoginRequiredMixin, ListView):
    '''Оплаченные заказы'''
    template_name = 'seller_site/list_order.html'
    paginate_by = 10
    queryset = OfflineOrderingProduct.objects.all().order_by('-datetime')
    context_object_name = 'queryset'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = OfflineCategory.objects.all()
        context['users'] = User.objects.all() 
        context['cash_seller'] = self.seller_filter() 
        context['form'] = OrderChangeForm()
        context['title'] = 'Заказы'
        return context

    def post(self, request):
        '''Изменяет кол-во товара в чеке'''
        if 'sold_id' not in request.POST and 'sold_count' not in request.POST and 'order_id':
            messages.error(request, 'Ошибка обработки заказа!')
            return redirect('local_shop:list_product')

        sold_pk = request.POST.getlist('sold_id')
        sold_count = request.POST.getlist('sold_count')

        try:
            order_id = int(request.POST.get('order_id'))
            res = [(int(sold_pk[i]), int(sold_count[i])) for i in range(len(sold_pk))]
        except (ValueError, TypeError):
            messages.error(request, 'Ошибка обработки заказа!')
            return redirect('local_shop:list_product')

        for item in res:
            sold_product = get_object_or_404(OfflineSoldProduct, pk=item[0])
            sold_product.return_in_product(item[1])
        
        order = get_object_or_404(OfflineOrderingProduct, pk=order_id)
        if order.offlinesoldproduct_set.all().count() == 0:
            order.delete()
        else:
            sold_product.order.set_order_price()
        return redirect('local_shop:list_order')

    def seller_filter(self):
        '''Вывод чеков продавца из списка и сумму заработанного за день '''
        try:
            user_id = int(self.request.GET.get('user_id'))
            self.queryset = OfflineOrderingProduct.objects.filter(user__id=user_id).order_by('-datetime')
            sold_for_day_seller = OfflineSoldProduct.objects.filter(Q(user__id=user_id) & Q(date__gte=date.today()))
            return sum([x.price_for_seller * x.count for x in sold_for_day_seller])
        except (TypeError, ValueError, AttributeError):
            return None


    def get(self, request, *args, **kwargs):
        if 'seller_filter' in request.GET:
            self.seller_filter()
        return super(OfflineOrderView, self).get(request, *args, **kwargs)


@method_decorator(staff_member_required, name='dispatch')
class OfflineStatisticView(LoginRequiredMixin, View):
    '''Представления общей статистики по товарам'''
    template_name = 'seller_site/statistic.html'
    
    def get_context_data(self, **kwargs):
        context = {}
        context['title'] = 'Статистика'
        context['stat_dict'] = self.get_statistic()
        context['category'] = OfflineCategory.objects.all()
        context['sold_product'] = self.get_sold_stat()
        context['reception_product'] = self.get_reception_stat()
        context['range'] = len(self.get_reception_stat())
        return context

    def seller_stat(self):
        User.objects.annotate(s=Sum(F('offlinesoldproduct__count')*F('offlinesoldproduct__price_for_seller'))) # сумма

    def get_reception_stat(self):
        '''Статистика каждого товара по приемке'''
        return OfflineProduct.objects.annotate(reception_count=Sum('offlinereceptionproduct__count')).annotate(reception_sum=F('purchase_price') * F('reception_count')).order_by('-reception_count')

    def get_sold_stat(self):
        '''Статистика каждого товара по продажам'''
        return OfflineProduct.objects.annotate(sold_count=Sum('offlinesoldproduct__count')).annotate(sold_sum=F('price') * F('sold_count')).order_by('-sold_count') 

    def get_statistic(self):
        '''Общая статистика магазина'''
        stat_dict = {'sold_stat' :[int(x or 0) for x in tuple(self.sold_queryset.annotate(sold_sum=F('count') * F('price')).aggregate(all_sold_price = Sum('sold_sum'),all_sold_count = Sum('count')).values())],
                     'reception_stat' :[int(x or 0) for x in tuple(self.reception_queryset.filter(liquidated=False).annotate(reception_sum=F('count') * F('price')).aggregate(all_reception_price= Sum('reception_sum'), all_reception_count=Sum('count')).values())],
                     'liquidated_stat':[int(x or 0) for x in tuple(self.reception_queryset.filter(liquidated=True).annotate(reception_sum=F('count') * F('price')).aggregate(all_reception_price= Sum('reception_sum'), all_reception_count=Sum('count')).values())]}
        stat_dict['all_stat'] = stat_dict['sold_stat'][0] - stat_dict['reception_stat'][0] - stat_dict['liquidated_stat'][0]
        return stat_dict


    def get_params(self):
        return {k:v for k,v in self.request.GET.items() if v != ''}

    def get_queryset(self):
        '''Фильтрует queryset по дате'''
        params = self.get_params()
        self.sold_queryset = OfflineSoldProduct.objects.all()
        self.reception_queryset = OfflineReceptionProduct.objects.all()

        if 'start' in params and 'end' in params:
            self.sold_queryset = self.sold_queryset.filter(date__range=[params['start'], params['end']])
            self.reception_queryset = self.reception_queryset.filter(date__range=[params['start'], params['end']])
        elif 'start' in params:
            self.sold_queryset = self.sold_queryset.filter(date__gte=params['start'])
            self.reception_queryset =self. reception_queryset.filter(date__gte=params['start'])
        elif 'end' in params:
            self.sold_queryset = self.sold_queryset.filter(date__lte=params['end'])
            self.reception_queryset = self.reception_queryset.filter(date__lte=params['end'])      

    def get(self, request):
        self.get_queryset()
        return render(request, self.template_name, context=self.get_context_data())


class OfflineSellerPage(LoginRequiredMixin, View):
    '''Представление для отображения продаж за день'''
    template_name = 'seller_site/seller_page.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['title'] = 'Продажи за день'
        context['category'] = OfflineCategory.objects.all()
        context['queryset'] = self.get_queryset()
        context['sum_for_seller'] = self.get_sum_for_seller()
        return context

    def get_sum_for_seller(self):
        '''Вычисляет сумму заработка продавца за день'''
        queryset = OfflineSoldProduct.objects.filter(Q(user=self.request.user) & Q(date__gte=date.today()))
        return sum([x.price_for_seller * x.count for x in queryset])


    def get_queryset(self):
        return OfflineOrderingProduct.objects.filter(Q(user=self.request.user) & Q(datetime__gte=date.today())).order_by('-datetime')

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data())



def change_item_order(request, sold_pk):
    instance = OfflineSoldProduct.objects.get(pk=sold_pk)
    form = OrderChangeForm(request.POST)
    if form.is_valid():
        cf = form.cleaned_data
        instance.return_in_product(cf['count'])
    instance.order.set_order_price()
    return redirect('local_shop:list_order')


def remove_item_order(request, sold_pk):
    instance = OfflineSoldProduct.objects.get(pk=sold_pk)
    order = instance.order
    instance.delete()
    order.set_order_price()
    return redirect('local_shop:list_order')

def delete_order(request, order_pk):
    order = OfflineOrderingProduct.objects.get(pk=order_pk)
    for item in order.offlinesoldproduct_set.all():
        item.delete()
    order.delete()
    return redirect('local_shop:list_order')