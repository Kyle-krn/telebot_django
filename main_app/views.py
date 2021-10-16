from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from .models import *
from django.http import HttpResponseRedirect
from django.contrib import messages
from itertools import chain
from django.db.models import Q
from datetime import date
from main_app.management.commands.utils import get_qiwi_balance
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views import View


class LoginUser(LoginView):
    '''Аутенификация пользователя'''
    form_class = LoginUserForm
    template_name = 'main_app/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Логин'
        return context

    def get_success_url(self):
        return reverse_lazy('all_product')


def logout_user(request):
    '''Выход'''
    logout(request)
    return redirect('login')


class IndexView(ListView):
    '''Вывод всех товаров'''
    context_object_name = 'product'
    template_name = 'main_app/index.html'

    def get_queryset(self):
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

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.all()
        return context

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().get(request)



class CreateProductView(LoginRequiredMixin, CreateView):
    '''Создание нового товара'''
    template_name = 'main_app/add_product.html'
    form_class = ProductForm   

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.all()
        return context


class ReceptionProductView(LoginRequiredMixin, CreateView):
    '''Представление добавления кол-ва товара (приемка)'''
    template_name = 'main_app/reception.html'
    form_class = ReceptionForm
    success_url = reverse_lazy('reception')

    def form_valid(self, form):
        product = Product.objects.get(pk=int(self.request.POST['product_pk']))
        product.count += form.cleaned_data['count']
        product.save()
        f = form.save(commit=False)
        f.product = product
        f.save()
        messages.info(self.request, 'Успешно!')
        return super().form_valid(form)


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subcategory'] = SubCategory.objects.all()
        return context



class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    '''Обновить категорию'''
    model = Category
    template_name = 'main_app/category_detail.html'
    form_class = Category_reqForm
    success_url = reverse_lazy('add_category')

    def get(self, *args, **kwargs):
        if 'delete' in self.request.GET:
            messages.info(self.request, 'Вы уверены?')
        if 'confirm_delete' in self.request.GET:
            category = self.get_object()
            category.delete()
            return redirect('add_category')  
        return super().get(self)








class CategoriesView(LoginRequiredMixin, View):
    template_name = 'main_app/category.html'
    queryset = Category.objects.all()

    def get_context_data(self, **kwargs):
        context = {}
        context['title'] = 'Категории'
        context['queryset'] = self.queryset
        context['category_form'] = CategoryForm()
        context['sc_form'] = SubcategoryForm()
        return context

    def post(self, request):
        if 'create_category' in request.POST:   # Создать категорию
            category_form = CategoryForm(request.POST, files=request.FILES)
            if category_form.is_valid():
                category_form.save()
                messages.info(request, 'Новая категория успешно создана!')
                return redirect('add_category')
        elif 'create_sc' in request.POST:   # Создать подкатеогрию
            sc_form = SubcategoryForm(request.POST, files=request.FILES)
            if sc_form.is_valid():
                f = sc_form.save(commit=False)    
                f.category = Category.objects.get(pk=int(request.POST['category_id']))
                f.save()
                messages.info(request, 'Новая подкатегория успешно создана!')
                return redirect('add_category')

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data())


class NoPaidOrderView(ListView):
    '''Неоплаченные заказы'''
    template_name = 'main_app/manager_order.html'
    queryset = OrderingProduct.objects.filter(payment_bool=False).order_by('-datetime')
    context_object_name = 'queryset'

    def post(self, request):
        if 'paid_status' in request.POST:
            order_id = int(request.POST['order_id'])
            order = OrderingProduct.objects.get(pk=order_id)
            if request.POST['payment'] == 'paid':        
                for item in order.sold_product.all():
                    item.product.count -= item.count
                    item.product.save()
                    item.payment_bool = True
                    item.save()
                order.payment_bool = True
                order.save()
                messages.add_message(request,messages.SUCCESS, 'Заказ успешно обработан!')
            else:
                order.sold_product.all().delete()
                order.delete()
                messages.add_message(request,messages.SUCCESS, 'Заказ успешно удален!')

        elif 'change_order' in request.POST:
            list_id = request.POST.getlist('product_id')
            list_count = request.POST.getlist('product_count')
            tuple_product = [(int(list_id[i]), int(list_count[i])) for i in range(len(list_id))]
            for item in tuple_product:
                if item[1] <= 0:
                    SoldProduct.objects.get(pk=item[0]).delete()
                else:
                    SoldProduct.objects.filter(pk=item[0]).update(count=item[1])
            messages.add_message(request,messages.SUCCESS, 'Заказ успешно изменен!')
        return redirect('new_order')




class PaidOrderView(ListView):
    '''Оплаченные заказы'''
    template_name = 'main_app/manager_order.html'
    queryset = OrderingProduct.objects.filter(payment_bool=True).order_by('-datetime')
    context_object_name = 'queryset'

    def post(self, request):
        order_id = int(request.POST['order_id'])
        order = OrderingProduct.objects.get(pk=order_id)
        track_code = request.POST['track_code']
        order.track_code = track_code
        order.save()
        messages.add_message(request,messages.SUCCESS, 'Трек номер успешно добавлен!')
        return redirect('old_order')


class StatisticView(LoginRequiredMixin, View):
    '''Представления общей статистики по товарам'''
    template_name = 'main_app/user_stat.html'
    sold_queryset = SoldProduct.objects.filter(payment_bool=True)
    reception_queryset = ReceptionProduct.objects.all()

    def get_context_data(self, **kwargs):
        context = {}
        context['title'] = 'Статистика'
        context['users'] = TelegramUser.objects.all().count()
        context['stat_dict'] = self.get_statistic()
        return context

    def get_statistic(self):
        stat_dict = {'sold_stat' : (sum([x.count * x.price for x in self.sold_queryset]), sum([x.count for x in self.sold_queryset])),
                 'reception_stat' : (sum([x.count * x.price for x in self.reception_queryset.filter(liquidated=False)]), sum([x.count for x in self.reception_queryset.filter(liquidated=False)])),
                 'liquidated_stat': (sum([x.count * x.price for x in self.reception_queryset.filter(liquidated=True)]) ,sum([x.count for x in self.reception_queryset.filter(liquidated=True)]))}
        stat_dict['all_stat'] = stat_dict['sold_stat'][0] - stat_dict['reception_stat'][0] - stat_dict['liquidated_stat'][0]
        return stat_dict

    def get_params(self):
        return {k:v for k,v in self.request.GET.items() if v != ''}

    def get_queryset(self):
        params = self.get_params()
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
        if 'start' in self.get_params() or 'end' in self.get_params():
            self.get_queryset()
        return render(request, self.template_name, context=self.get_context_data())


class ProductView(View):
    template_name = 'main_app/product.html'
    
    def get_object(self):
        self.product = get_object_or_404(Product, pk=self.kwargs.get('pk'))


    def get_params(self):
        return {k:v for k,v in self.request.GET.items() if v != ''}

    def filter_queryset(self):
        params = self.get_params()
        if 'only' in params:
            if params['only'] == 'reception':
                result_list = self.reception_queryset.filter(liquidated=False)
            elif params['only'] == 'sold':
                result_list = self.sold_queryset
            elif params['only'] == 'liquidated':
                result_list = self.reception_queryset.filter(liquidated=True)
        else:
            result_list = sorted(
                    chain(self.reception_queryset, self.sold_queryset),
                    key=lambda instance: instance.date, reverse=True)
        return result_list

    def get_queryset(self, pk):
        params = self.get_params()
        self.reception_queryset = ReceptionProduct.objects.filter(product__pk=pk)
        self.sold_queryset = SoldProduct.objects.filter(Q(product__pk=pk) & Q(payment_bool=True))

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

    def get_context_data(self, **kwargs):
        context = {}
        context['product'] = self.product
        context['category'] = Category.objects.all()
        context['reception_form'] = ReceptionForm()
        context['stat_dict'] = self.get_statistic()
        context['trade_queryset'] = self.filter_queryset()
        context['product_form'] = Product_reqForm(initial={'title': self.product.title,
                                        'description': self.product.description,
                                        'price': self.product.price,
                                        'weight': self.product.weight,
                                        'subcategory': self.product.subcategory_id})
        return context

    def post(self, request, pk):
        self.get_object()
        self.get_queryset(pk)

        if 'update' in request.POST:
            product_form = Product_reqForm(request.POST, files=request.FILES, instance=self.product)
            if product_form.is_valid():
                product_form.save()
                return redirect('productdetail', pk=pk)

        elif 'delete' in request.POST:
            messages.info(request, 'Вы уверены?')
            return redirect('productdetail', pk=pk)

        elif 'confirm_delete' in request.POST:
            self.product.delete()
            return redirect ('all_product')

        elif 'reception' in request.POST:
            form = ReceptionForm(request.POST)
            print(form.is_valid())
            if form.is_valid():
                self.product.count += form.cleaned_data['count']
                self.product.save()
                f = form.save(commit=False)
                f.product = self.product
                f.save()
                return redirect('productdetail', pk=pk)           

        elif 'liquidated' in request.POST:
            count = int(request.POST['liquidated_count'])
            note = request.POST['liquidated_note']
            ReceptionProduct.objects.create(price=int(request.POST['liquidated_price']), count=count, note=note, product=self.product, liquidated=True)
            self.product.count -= count
            self.product.save()
            return redirect('productdetail', pk=pk) 
        

    
    def get(self, request, pk):
        self.get_object()
        self.get_queryset(pk)
        return render(request, self.template_name, context=self.get_context_data())

@login_required
def product_view(request, pk):
    '''Страница изменения продукта/добавления кол-ва в товар и списание'''
    product = get_object_or_404(Product, pk=pk)
    category = Category.objects.all()
    if request.method == "POST" and 'update' in request.POST:
        product_form = Product_reqForm(request.POST, files=request.FILES, instance=product)
        if product_form.is_valid():
            product_form.save()
            return redirect('productdetail', pk=pk)

    if request.method == "POST" and 'delete' in request.POST:
        messages.info(request, 'Вы уверены?')

    if request.method == 'POST' and 'confirm_delete' in request.POST:
        product.delete()
        return redirect('all_product')

    if request.method == 'POST':
        if 'reception' in request.POST:
            form = ReceptionForm(request.POST)
            print(form.is_valid())
            if form.is_valid():
                product.count += form.cleaned_data['count']
                product.save()
                f = form.save(commit=False)
                f.product = product
                f.save()
                return redirect('productdetail', pk=pk)

        elif 'liquidated' in request.POST:
            count = int(request.POST['liquidated_count'])
            note = request.POST['liquidated_note']
            ReceptionProduct.objects.create(price=int(request.POST['liquidated_price']), count=count, note=note, product=product, liquidated=True)
            product.count -= count
            product.save()
            return redirect('productdetail', pk=pk)

    reception_form = ReceptionForm()
    reception_queryset = ReceptionProduct.objects.filter(product__pk=pk)
    sold_queryset = SoldProduct.objects.filter(Q(product__pk=pk) & Q(payment_bool=True))

    

    params = {k:v for k,v in request.GET.items() if len(v) != 0}

    if 'start' in params and 'end' in params:
        sold_queryset = sold_queryset.filter(date__range=[params['start'], params['end']])
        reception_queryset = reception_queryset.filter(date__range=[params['start'], params['end']])
    elif 'start' in params:
        sold_queryset = sold_queryset.filter(date__gte=params['start'])
        reception_queryset = reception_queryset.filter(date__gte=params['start'])
    elif 'end' in params:
        sold_queryset = sold_queryset.filter(date__lte=params['end'])
        reception_queryset = reception_queryset.filter(date__lte=params['end'])      

    stat_dict = {
        'sold_stat': (sum([x.count * x.price for x in sold_queryset]), sum([x.count for x in sold_queryset])),
        'reception_stat': (sum([x.count * x.price for x in reception_queryset.filter(liquidated=False)]), sum([x.count for x in reception_queryset.filter(liquidated=False)])),
        'liquidated_stat': (sum([x.count * x.price for x in reception_queryset.filter(liquidated=True)]) ,sum([x.count for x in reception_queryset.filter(liquidated=True)]))
    }
    stat_dict['all_stat'] = stat_dict['sold_stat'][0] - stat_dict['reception_stat'][0] - stat_dict['liquidated_stat'][0]

    if 'only' in params:
        if params['only'] == 'reception':
            result_list = reception_queryset.filter(liquidated=False)
        elif params['only'] == 'sold':
            result_list = sold_queryset
        elif params['only'] == 'liquidated':
            result_list = reception_queryset.filter(liquidated=True)
    else:
        result_list = sorted(
                chain(reception_queryset, sold_queryset),
                key=lambda instance: instance.date, reverse=True)


    product_form = Product_reqForm(initial={'title': product.title,
                                        'description': product.description,
                                        'price': product.price,
                                        'weight': product.weight,
                                        'subcategory': product.subcategory_id})
                                        
    return render(request, 'main_app/product.html', {'product_form': product_form,
                                                     'product': product,
                                                     'category': category,
                                                     'reception_form': reception_form,
                                                     'trade_queryset': result_list,

                                                     'stat_dict': stat_dict
                                                     })


def control_qiwi(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST' and 'new_token' in request.POST:
        form = QiwiTokenForm(request.POST)
        try:
            balance = get_qiwi_balance(request.POST['number'], request.POST['token'])
            if form.is_valid():
                qiwi = form.save()
                qiwi.balance = balance
                qiwi.save()
        except:
            messages.info(request, 'Ошибка получения баланса кошелька')
    elif request.method == 'POST' and 'activate' in request.POST:
        QiwiToken.objects.update(active=False)
        qiwi_id = int(request.POST['radio'])
        QiwiToken.objects.filter(pk=qiwi_id).update(active=True)
    elif request.method == 'POST' and 'del_tok' in request.POST:
        qiwi_id = int(request.POST['del_tok_list'])
        QiwiToken.objects.get(pk=qiwi_id).delete()

    pay_product = PayProduct.objects.all()
    queryset = QiwiToken.objects.all()
    form = QiwiTokenForm()
    return render(request, 'main_app/qiwi.html', context={'form': form, 'queryset': queryset, 'pay_product': pay_product})
