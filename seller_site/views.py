from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .models import *
from django.contrib import messages
from .forms import *
from django.views.generic.edit import UpdateView, CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import ListView
from itertools import chain
from collections import Counter
from django.db.models import Count, Sum


def make_order_view(request):
    '''Представление для формы продажи'''
    if request.method == 'POST':
        if 'product_id' not in request.POST and 'product_count' not in request.POST:
            return redirect('all_product_offline')

        pk_list = request.POST.getlist('product_id')    
        count_list = request.POST.getlist('product_count')

        if len(pk_list) != len(count_list):     # Доп проверка
            return redirect('all_product_offline')

        try:
            l_list = [(int(pk_list[i]), int(count_list[i])) for i in range(len(pk_list))]
        except ValueError:
            return redirect('all_product_offline')

        c = Counter()
        for item in l_list:         # Прогоняем через Counter что бы не плодить одинаковые товары в чеке
            c[item[0]] += item[1]
        l_list = c.most_common()        
        order = OfflineOrderingProduct.objects.create(user=request.user)    # Создаем чек
        for item in l_list: # Добавляем проданные товары в чек
            product = OfflineProduct.objects.get(pk=item[0])
            sold_product = OfflineSoldProduct.objects.create(product=product ,price=product.price, count=item[1])
            order.sold_product.add(sold_product)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))   # Возвращаем юзера обратно 
    else:
        return redirect('all_product_offline')


def reception_view(request):
    '''Представление для формы приемки товара'''
    if request.method == 'POST':
        if 'count_reception' not in request.POST and 'note_reception' not in request.POST and 'product_id' not in request.POST:
            return redirect('all_product_offline')

        try:
            count =int(request.POST.get('count_reception'))
            product_pk = int(request.POST.get('product_id'))
            note = request.POST.get('note_reception')
        except ValueError:
            return redirect('all_product_offline')
        
        product = OfflineProduct.objects.get(pk=product_pk)
        OfflineReceptionProduct.objects.create(product=product, user=request.user, note=note, price=product.purchase_price, count=count)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('all_product_offline')


class OfflineCategoriesView(LoginRequiredMixin, View):
    '''Представление создания/просмотра категорий/подкатегорий'''
    template_name = 'seller_site/offline_category.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['title'] = 'Категории (Оффлайн магазин)'
        context['category'] = OfflineCategory.objects.all()
        context['category_form'] = OffilneCategoryForm()
        context['category_change_form'] = OffilneChangeCategoryForm()
        context['sc_form'] = OfflineSubcategoryForm()
        return context

    def post(self, request):
        if 'create_category' in request.POST:   # Создать категорию
            category_form = OffilneCategoryForm(request.POST)
            if category_form.is_valid():
                category_form.save()
                messages.info(request, 'Новая категория успешно создана!')
                
        
        elif 'change_category' in request.POST:
            if 'category_pk' not in request.POST and 'category_name' not in request.POST and 'category_price_for_seller' not in request.POST:
                return redirect('all_product_offline')
            
            try:
                category_pk = int(request.POST.get('category_pk'))
                name = request.POST.get('category_name')
                price_for_seller = request.POST.get('category_price_for_seller')
            except ValueError:
                return redirect('all_product_offline')

            category = OfflineCategory.objects.get(pk=category_pk)  # Изменить на update
            category.name = name
            category.price_for_seller = price_for_seller                                 #   
            category.save()                                         #
            messages.info(request, 'Категория  успешно изменена!')

        elif 'delete_category' in request.POST:
            if 'category_pk' not in request.POST:
                return redirect('all_product_offline')
            
            try:
                category_pk = int(request.POST.get('category_pk'))
            except ValueError:
                return redirect('all_product_offline')

            OfflineCategory.objects.get(pk=category_pk).delete()
            messages.info(request, 'Категория успешно удалена!')

        elif 'create_sc' in request.POST:   # Создать подкатеогрию
            sc_form = OfflineSubcategoryForm(request.POST)
            if sc_form.is_valid():
                f = sc_form.save(commit=False)    
                f.category = OfflineCategory.objects.get(pk=int(request.POST['category_id']))
                f.save()
                messages.info(request, 'Новая подкатегория успешно создана!')

        elif 'change_subcategory' in request.POST:
            if 'subcategory_pk' not in request.POST and 'subcategory_name' not in request.POST:
                return redirect ('all_product_offline')

            try:
                subcategory_pk = int(request.POST.get('subcategory_pk'))
                subcategory_name = request.POST.get('subcategory_name')
            except ValueError:
                return redirect('all_product_offline')

            subcategory = OfflineSubCategory.objects.get(pk=subcategory_pk) # Изменить на update
            subcategory.name = subcategory_name
            subcategory.save()
            messages.info(request, 'Подкатегория успешно изменена!')

        elif 'delete_subcategory' in request.POST:
            if 'subcategory_pk' not in request.POST:
                return redirect('all_product_offline')
            
            try:
                subcategory_pk = int(request.POST.get('subcategory_pk'))
            except ValueError:
                return redirect('all_product_offline')

            OfflineSubCategory.objects.get(pk=subcategory_pk).delete()
            messages.info(request, 'Подкатегория успешно удалена!')
            
        return redirect('category_offline')

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data())


class OfflineCategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    '''Обновить категорию'''
    model = OfflineCategory
    template_name = 'seller_site/offline_category_detail.html'
    form_class = OffilneCategoryForm
    success_url = reverse_lazy('category_offline')
    success_message = 'Категория успешно обновлена!'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Изменить категорию/подкатегорию'
        return context


    def post(self, *args, **kwargs):
        if 'delete' in self.request.POST:
            category = self.get_object()
            category.delete()
            return redirect('category_offline')
        return super().post(self)


class OfflineCreateProductView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    '''Создание нового товара'''
    template_name = 'seller_site/offline_add_product.html'
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
    template_name = 'seller_site/offline_all_product.html'

    def post(self, request):
        if 'delete_product' in request.POST:
            if 'pk_p' not in request.POST:
                return redirect('all_product_offline')

            try:
                pk_product = int(request.POST.get('pk_p'))
            except ValueError:
                return redirect('all_product_offline')

            OfflineProduct.objects.get(pk=pk_product).delete()
            return redirect('all_product_offline')

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



class OfflineProductAdminView(LoginRequiredMixin, View):
    '''Детальное представление товара и управление им'''
    template_name = 'seller_site/offline_product.html'
    
    def get_object(self):
        self.product = get_object_or_404(OfflineProduct, pk=self.kwargs.get('pk'))

    def get_params(self):
        return {k:v for k,v in self.request.GET.items() if v != ''}

    def get_context_data(self, **kwargs):
        context = {}
        context['product'] = self.product
        context['title'] = self.product.title
        context['category'] = OfflineCategory.objects.all()
        context['reception_form'] = OfflineReceptionForm()
        context['stat_dict'] = self.get_statistic()
        context['trade_queryset'] = self.filter_queryset()
        context['product_form'] = OfflineProductForm(initial={'title': self.product.title,
                                        'price': self.product.price,
                                        'purchase_price': self.product.purchase_price,
                                        'subcategory': self.product.subcategory_id})
        return context

    def filter_queryset(self):
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
        stat_dict = {
            'sold_stat': (sum([x.count * x.price for x in self.sold_queryset]), sum([x.count for x in self.sold_queryset])),
            'reception_stat': (sum([x.count * x.price for x in self.reception_queryset.filter(liquidated=False)]), sum([x.count for x in self.reception_queryset.filter(liquidated=False)])),
            'liquidated_stat': (sum([x.count * x.price for x in self.reception_queryset.filter(liquidated=True)]) ,sum([x.count for x in self.reception_queryset.filter(liquidated=True)]))
        }
        stat_dict['all_stat'] = stat_dict['sold_stat'][0] - stat_dict['reception_stat'][0]
        return stat_dict

    def post(self, request, pk):
        self.get_object()
        if 'update' in request.POST:
            product_form = OfflineProductForm(request.POST, instance=self.product)
            if product_form.is_valid():
                product_form.save()
                messages.info(request, 'Товар успешно обновлен!')
                return redirect('product_detail_offline', pk=pk)

        elif 'delete' in request.POST:
            self.product.delete()
            messages.info(request, 'Товар усппешно удален!')
            return redirect ('all_product_offline')

        elif 'reception' in request.POST:
            form = OfflineReceptionForm(request.POST)
            if form.is_valid():
                f = form.save(commit=False)
                f.product = self.product
                f.price = self.product.purchase_price
                f.user = request.user
                f.save()
                messages.info(request, 'Количество товара успешно увеличено!')
                return redirect('product_detail_offline', pk=pk)

        elif 'liquidated' in request.POST:
            form = OfflineReceptionForm(request.POST)
            if form.is_valid():
                f = form.save(commit=False)
                f.product = self.product
                f.price = self.product.purchase_price
                f.user = request.user
                f.liquidated = True
                f.save()
                messages.info(request, 'Товар успешно списан!')
                return redirect('product_detail_offline', pk=pk)
 
    def get(self, request, pk):
        self.get_object()
        self.get_queryset(pk)
        return render(request, self.template_name, context=self.get_context_data())


class OfflineOrderView(ListView):
    '''Оплаченные заказы'''
    template_name = 'seller_site/offline_order.html'
    queryset = OfflineOrderingProduct.objects.all().order_by('-datetime')
    context_object_name = 'queryset'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = OfflineCategory.objects.all()
        context['title'] = 'Заказы'
        return context

    def post(self, request):
        if 'sold_id' not in request.POST and 'sold_count' not in request.POST:
            return redirect('all_product_offline')

        sold_pk = request.POST.getlist('sold_id')
        sold_count = request.POST.getlist('sold_count')

        try:
            res = [(int(sold_pk[i]), int(sold_count[i])) for i in range(len(sold_pk))]
        except ValueError:
            return redirect('all_product_offline')

        for item in res:
            sold_product = OfflineSoldProduct.objects.get(pk=item[0])
            sold_product.return_in_product(request, item[1])
        return redirect('order_offline')

    def get(self, request, *args, **kwargs):
        return super(OfflineOrderView, self).get(request, *args, **kwargs)


class OfflineStatisticView(LoginRequiredMixin, View):
    '''Представления общей статистики по товарам'''
    template_name = 'seller_site/offline_statistic.html'
    
    def get_context_data(self, **kwargs):
        context = {}
        context['title'] = 'Статистика'
        context['stat_dict'] = self.get_statistic()
        context['category'] = OfflineCategory.objects.all()
        context['product'] = OfflineProduct.objects.annotate(sold_count=Sum('offlinesoldproduct__count')).order_by('-sold_count')
        return context

    def get_statistic(self):
        stat_dict = {'sold_stat' : (sum([x.count * x.price for x in self.sold_queryset]), sum([x.count for x in self.sold_queryset])),
                 'reception_stat' : (sum([x.count * x.price for x in self.reception_queryset.filter(liquidated=False)]), sum([x.count for x in self.reception_queryset.filter(liquidated=False)])),
                 'liquidated_stat': (sum([x.count * x.price for x in self.reception_queryset.filter(liquidated=True)]) ,sum([x.count for x in self.reception_queryset.filter(liquidated=True)]))}
        stat_dict['all_stat'] = stat_dict['sold_stat'][0] - stat_dict['reception_stat'][0] - stat_dict['liquidated_stat'][0]
        print(stat_dict)
        return stat_dict

    def get_params(self):
        return {k:v for k,v in self.request.GET.items() if v != ''}

    def get_queryset(self):
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


class OfflineSellerPage(View):
    template_name = 'seller_site/offline_seller_page.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['title'] = 'Продажи за день'
        context['category'] = OfflineCategory.objects.all()
        context['queryset'] = self.get_queryset()
        context['sum_for_seller'] = self.get_sum_for_seller()
        return context

    def get_sum_for_seller(self):
        return sum([i2.count * i2.product.subcategory.category.price_for_seller for i in [i.sold_product.all() for i in OfflineOrderingProduct.objects.filter(user=self.request.user)] for i2 in i])

    def get_queryset(self):
        return OfflineOrderingProduct.objects.filter(user=self.request.user)

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data())


# [(i2.count, i2.product.subcategory.category.price_for_seller) for i in [i.sold_product.all() for i in OfflineOrderingProduct.objects.all()] for i2 in i] для расчета зп сотрудника

# OfflineProduct.objects.annotate(sold_count=Sum('offlinesoldproduct__count'))

