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
    product = Product.objects.get(pk=pk)
    category = Category.objects.all()
    if request.method == "POST" and 'update' in request.POST:
        instance = get_object_or_404(Product, pk=pk)
        product_form = ProductForm(request.POST, files=request.FILES, instance=instance)
        if product_form.is_valid():
            product_form.save()
            return HttpResponseRedirect('/')

    if request.method == "POST" and 'delete' in request.POST:
        messages.info(request, 'Вы уверены?')

    if request.method == 'GET' and 'confirm_delete' in request.GET:
        # Сделать удаление товара здесь
        return HttpResponseRedirect('/')

    product_form = ProductForm(initial={'title': product.title,
                                        'description': product.description,
                                        'price': product.price,
                                        'count': product.count,
                                        'subcategory': product.subcategory_id})
    return render(request, 'main_app/product.html', {'product_form': product_form, 'product': product, 'category': category})


def create_category(request):
    if request.method == 'POST' and 'create_category' in request.POST:
        category_form = CategoryForm(request.POST, files=request.FILES)
        print(category_form.is_valid())
        if category_form.is_valid():
            category_form.save()
            messages.info(request, 'Новая категория успешно создана!')
            return HttpResponseRedirect('/add_category/')
        else:
            messages.info(request, 'Ошибка!')
            return HttpResponseRedirect('/add_category/')

    category_form = CategoryForm()
    sc_form = SubcategoryForm()
    category = Category.objects.all()

    return render(request, 'main_app/category.html', {'category_form': category_form, 'sc_form': sc_form ,'category': category})