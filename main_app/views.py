from django.shortcuts import render, get_object_or_404
from .forms import *
from .models import *
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
import json



def index(request):
    product = Product.objects.all()
    category = Category.objects.all()
    return render(request, 'main_app/index.html', {'product': product})


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
        # Сделать удаление товара здесь
        return HttpResponseRedirect('/')

    product_form = Product_reqForm(initial={'title': product.title,
                                        'description': product.description,
                                        'price': product.price,
                                        'count': product.count,
                                        'subcategory': product.subcategory_id})
    return render(request, 'main_app/product.html', {'product_form': product_form, 'product': product, 'category': category})


def create_product(request):
    if request.method == "POST":
        product_form = ProductForm(request.POST, files=request.FILES)
        if product_form.is_valid():
            product_form.save()
            return HttpResponseRedirect('/')

    product_form = ProductForm(initial={'count': 0})
    category = Category.objects.all()
    return render(request, 'main_app/product.html', {'product_form': product_form, 'category': category})


def create_category(request):
    if request.method == 'POST' and 'create_category' in request.POST:
        category_form = CategoryForm(request.POST, files=request.FILES)
        if category_form.is_valid():
            category_form.save()
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


    category_form = Category_reqForm(initial={'name': category.name})
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