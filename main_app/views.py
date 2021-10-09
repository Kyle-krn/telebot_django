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

def index(request):
    '''Вывод всех товаров на главной странице'''
    if not request.user.is_authenticated:
        return redirect('login')
    product = Product.objects.all()
    category = Category.objects.all()
    if 'search' in request.GET:
        params = {k:v for k,v in request.GET.items() if len(v) != 0}
        print(params)
        if 'title' in params:
            product = product.filter(title__icontains=params['title'])
        if 'category' in params:
            product = product.filter(subcategory__category__pk=int(params['category']))
        if 'subcategory' in params:
            product = product.filter(subcategory__pk=int(params['subcategory']))
        if 'order_by' in params:
            product = product.order_by(params['order_by'])
    return render(request, 'main_app/index.html', {'product': product, 'category': category})


def product_view(request, pk):
    '''Страница изменения продукта/добавления кол-ва в товар и списание'''
    if not request.user.is_authenticated:
        return redirect('login')
    product = get_object_or_404(Product, pk=pk)
    category = Category.objects.all()
    if request.method == "POST" and 'update' in request.POST:
        product_form = Product_reqForm(request.POST, files=request.FILES, instance=product)
        if product_form.is_valid():
            product_form.save()
            return redirect('productdetail', pk=pk)

    if request.method == "POST" and 'delete' in request.POST:
        messages.info(request, 'Вы уверены?')

    if request.method == 'GET' and 'confirm_delete' in request.GET:
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
    sold_queryset = SoldProduct.objects.filter(product__pk=pk)

    sold_stat = (sum([x.count * x.price for x in sold_queryset]), sum([x.count for x in sold_queryset]))
    reception_stat = (sum([x.count * x.price for x in reception_queryset]), sum([x.count for x in reception_queryset]))
    liquidated_stat = sum([x.count * x.price for x in reception_queryset.filter(liquidated=True)]) ,sum([x.count for x in reception_queryset.filter(liquidated=True)])
    all_stat = sold_stat[0] - reception_stat[0] - liquidated_stat[0]
    

    params = {k:v for k,v in request.GET.items() if len(v) != 0}

    if 'only' in params:
        print('here')
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
                                                     'sold_stat': sold_stat,
                                                     'reception_stat': reception_stat, 
                                                     'liquidated_stat': liquidated_stat,
                                                     'all_stat': all_stat,
                                                     })


def create_product(request):
    '''Страница создания товара'''
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == "POST":
        product_form = ProductForm(request.POST, files=request.FILES)
        if product_form.is_valid():
            product = product_form.save()
            product.slug = f'p||{product.pk}'
            product.save()
            return redirect('productdetail', pk=product.pk)

    product_form = ProductForm(initial={'count': 0})
    category = Category.objects.all()
    return render(request, 'main_app/add_product.html', {'product_form': product_form, 'category': category})


def reception_product(request):
    if not request.user.is_authenticated:
        return redirect('login')
    reception_form = ReceptionForm()
    return render(request, 'main_app/reception.html', {'reception_form': reception_form})


def create_category(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST' and 'create_category' in request.POST:
        category_form = CategoryForm(request.POST, files=request.FILES)
        if category_form.is_valid():
            model = category_form.save()
            model.slug = f'c||{model.pk}'
            model.save()
            messages.info(request, 'Новая категория успешно создана!')
            return redirect('add_category')
        else:
            messages.info(request, 'Ошибка!')
            return redirect('add_category')

    elif request.method == "POST" and 'create_sc' in request.POST:
        sc_form = SubcategoryForm(request.POST, files=request.FILES)
        if sc_form.is_valid():
            f = sc_form.save(commit=False)    
            f.category = Category.objects.get(pk=int(request.POST['category_id']))
            f.save()
            f.slug = f'sc||{f.pk}'
            f.save()
            messages.info(request, 'Новая категория успешно создана!')
            return redirect('add_category')

    category_form = CategoryForm()
    sc_form = SubcategoryForm()
    category = Category.objects.all()

    return render(request, 'main_app/category.html', {'category_form': category_form, 'sc_form': sc_form ,'category': category})


def category_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category_form = Category_reqForm(request.POST, files=request.FILES, instance=category)
        if category_form.is_valid():
            category_form.save()
        return redirect('add_category')
    
    if request.method == 'GET' and 'delete' in request.GET:
        messages.info(request, 'Вы уверены?')

    elif request.method == 'GET' and 'confirm_delete' in request.GET:
        messages.info(request, 'Категория успешно удалена')
        category.delete()
        return redirect('add_category')


    category_form = Category_reqForm(initial={'name': category.name, 'max_count_product': category.max_count_product})
    return render(request, 'main_app/category_detail.html', {'category': category, 'category_form': category_form})


def subcategory_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    subcategory = get_object_or_404(SubCategory, id=pk)
    if request.method == "POST":
        category_form = Subcategory_reqForm(request.POST, files=request.FILES, instance=subcategory)
        if category_form.is_valid():
            category_form.save()
        return redirect('add_category')
    
    if request.method == 'GET' and 'delete' in request.GET:
        messages.info(request, 'Вы уверены?')

    elif request.method == 'GET' and 'confirm_delete' in request.GET:
        messages.info(request, 'Категория успешно удалена')
        subcategory.delete()
        return redirect('add_category')

    category_form = Subcategory_reqForm(initial={'name': subcategory.name})
    return render(request, 'main_app/category_detail.html', {'category': subcategory, 'category_form': category_form})


def new_order(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        order_id = int(request.POST['order_id'])
        try:
            track_code = int(request.POST['track_number'])
        except:
            messages.info(request, 'Трек номер состоит только из цифр!')
            return HttpResponseRedirect('/new_order/')
        order = OrderingProduct.objects.get(pk=order_id)
        order.track_code = track_code
        order.check_admin = True
        order.save()
    title = 'Новые заказы'
    queryset = OrderingProduct.objects.filter(check_admin=False)
    return render(request, 'main_app/order.html', context={'queryset': queryset, 'title': title})

def old_order(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        order_id = int(request.POST['order_id'])
        try:
            track_code = int(request.POST['track_number'])
        except:
            messages.info(request, 'Трек номер состоит только из цифр!')
            return HttpResponseRedirect('/new_order/')
        order = OrderingProduct.objects.get(pk=order_id)
        order.track_code = track_code
        order.check_admin = True
        order.save()
    
    title = 'Обработанные заказы'
    queryset = OrderingProduct.objects.filter(check_admin=True)
    return render(request, 'main_app/order.html', context={'queryset': queryset, 'title': title})


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



def user_stat(request):
    if not request.user.is_authenticated:
        return redirect('login')
    users = TelegramUser.objects.all()
    sold_queryset = SoldProduct.objects.all()
    reception_queryset = ReceptionProduct.objects.all()
    params = {k:v for k,v in request.GET.items() if v != ''}

    if 'start' in params and 'end' in params:
        sold_queryset = sold_queryset.filter(date__range=[params['start'], params['end']])
        reception_queryset = reception_queryset.filter(date__range=[params['start'], params['end']])
    elif 'start' in params:
        sold_queryset = sold_queryset.filter(date__gte=params['start'])
        reception_queryset = reception_queryset.filter(date__gte=params['start'])
    elif 'end' in params:
        sold_queryset = sold_queryset.filter(date__lte=params['end'])
        reception_queryset = reception_queryset.filter(date__lte=params['end'])      

    sold_stat = (sum([x.count * x.price for x in sold_queryset]), sum([x.count for x in sold_queryset]))
    reception_stat = (sum([x.count * x.price for x in reception_queryset]), sum([x.count for x in reception_queryset]))
    liquidated_stat = sum([x.count * x.price for x in reception_queryset.filter(liquidated=True)]) ,sum([x.count for x in reception_queryset.filter(liquidated=True)])
    all_stat = sold_stat[0] - reception_stat[0] - liquidated_stat[0]

    return render(request, 'main_app/user_stat.html', context={'users': users, 'sold_stat': sold_stat, 'reception_stat': reception_stat, 'liquidated_stat': liquidated_stat, 'all_stat': all_stat})