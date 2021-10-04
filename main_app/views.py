from django.shortcuts import render, get_object_or_404
from .forms import *
from .models import *
from django.http import HttpResponseRedirect
from django.contrib import messages
from itertools import chain
from django.db.models import Q


def index(request):
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
        if 'from_price' in params:
            product = product.filter(price__gte=int(params['from_price']))
        if 'to_price' in params:
            product = product.filter(price__lte=int(params['to_price']))
        if 'from_count' in params:
            product = product.filter(count__gte=int(params['from_count']))
        if 'to_count' in params:
            product = product.filter(count__lte=int(params['to_count']))

        if 'order_by' in params:
            product = product.order_by(params['order_by'])
        
        
    return render(request, 'main_app/index.html', {'product': product, 'category': category})


def product_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    category = Category.objects.all()
    if request.method == "POST" and 'update' in request.POST:
        product_form = Product_reqForm(request.POST, files=request.FILES, instance=product)
        if product_form.is_valid():
            product_form.save()
            return HttpResponseRedirect('/')

    if request.method == "POST" and 'delete' in request.POST:
        messages.info(request, 'Вы уверены?')

    if request.method == 'GET' and 'confirm_delete' in request.GET:
        product.delete()
        return HttpResponseRedirect('/')

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
                return HttpResponseRedirect('/')

        elif 'liquidated' in request.POST:
            count = int(request.POST['liquidated_count'])
            note = request.POST['liquidated_note']
            ReceptionProduct.objects.create(price=0, count=count, note=note, product=product, liquidated=True)
            product.count -= count
            product.save()
            return HttpResponseRedirect('/')

    reception_form = ReceptionForm()
    reception_queryset = ReceptionProduct.objects.filter(product__pk=pk)
    sold_queryset = SoldProduct.objects.filter(product__pk=pk)

    # print(request.GET['birthday'])12

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
                                        
    return render(request, 'main_app/product.html', {'product_form': product_form, 'product': product, 'category': category, 'reception_form': reception_form, 'trade_queryset': result_list})


def create_product(request):
    if request.method == "POST":
        product_form = ProductForm(request.POST, files=request.FILES)
        if product_form.is_valid():
            product = product_form.save()
            product.slug = f'p||{product.pk}'
            product.save()
            return HttpResponseRedirect('/')

    product_form = ProductForm(initial={'count': 0})
    category = Category.objects.all()
    return render(request, 'main_app/add_product.html', {'product_form': product_form, 'category': category})


def reception_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reception_form = ReceptionForm()
    return render(request, 'main_app/reception.html', {'reception_form': reception_form})


def create_category(request):
    if request.method == 'POST' and 'create_category' in request.POST:
        category_form = CategoryForm(request.POST, files=request.FILES)
        if category_form.is_valid():
            model = category_form.save()
            model.slug = f'c||{model.pk}'
            model.save()
            messages.info(request, 'Новая категория успешно создана!')
            return HttpResponseRedirect('/add_category/')
        else:
            messages.info(request, 'Ошибка!')
            return HttpResponseRedirect('/add_category/')

    elif request.method == "POST" and 'create_sc' in request.POST:
        sc_form = SubcategoryForm(request.POST, files=request.FILES)
        if sc_form.is_valid():
            f = sc_form.save(commit=False)    
            f.category = Category.objects.get(pk=int(request.POST['category_id']))
            f.save()
            f.slug = f'sc||{f.pk}'
            f.save()
            messages.info(request, 'Новая категория успешно создана!')
            return HttpResponseRedirect('/add_category/')

    category_form = CategoryForm()
    sc_form = SubcategoryForm()
    category = Category.objects.all()

    return render(request, 'main_app/category.html', {'category_form': category_form, 'sc_form': sc_form ,'category': category})


def category_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category_form = Category_reqForm(request.POST, files=request.FILES, instance=category)
        if category_form.is_valid():
            category_form.save()
        return HttpResponseRedirect('/add_category')
    
    if request.method == 'GET' and 'delete' in request.GET:
        messages.info(request, 'Вы уверены?')

    elif request.method == 'GET' and 'confirm_delete' in request.GET:
        messages.info(request, 'Категория успешно удалена')
        category.delete()
        return HttpResponseRedirect('/add_category/')


    category_form = Category_reqForm(initial={'name': category.name, 'max_count_product': category.max_count_product})
    return render(request, 'main_app/category_detail.html', {'category': category, 'category_form': category_form})


def subcategory_view(request, pk):
    subcategory = get_object_or_404(SubCategory, id=pk)
    if request.method == "POST":
        category_form = Subcategory_reqForm(request.POST, files=request.FILES, instance=subcategory)
        if category_form.is_valid():
            category_form.save()
        return HttpResponseRedirect('/add_category')
    
    if request.method == 'GET' and 'delete' in request.GET:
        messages.info(request, 'Вы уверены?')

    elif request.method == 'GET' and 'confirm_delete' in request.GET:
        messages.info(request, 'Категория успешно удалена')
        subcategory.delete()
        return HttpResponseRedirect('/add_category/')

    category_form = Subcategory_reqForm(initial={'name': subcategory.name})
    return render(request, 'main_app/category_detail.html', {'category': subcategory, 'category_form': category_form})