from django.shortcuts import render, get_object_or_404
from .forms import *
from .models import *
from django.http import HttpResponseRedirect, HttpResponse
import json



def index(request):
    product = Product.objects.all()
    category = Category.objects.all()
    return render(request, 'main_app/index.html', {'product': product})


def product_view(request, pk):
    product = Product.objects.get(pk=pk)
    category = Category.objects.all()
    if request.method == "POST":
        instance = get_object_or_404(Product, pk=pk)
        product_form = ProductForm(request.POST, files=request.FILES, instance=instance)
        if product_form.is_valid():
            product_form.save()
            return HttpResponseRedirect('/')
    else:
        product_form = ProductForm(initial={'title': product.title,
                                            'description': product.description,
                                            'price': product.price,
                                            'count': product.count,
                                            'subcategory': product.subcategory_id})
    return render(request, 'main_app/product.html', {'product_form': product_form, 'product': product, 'category': category})
