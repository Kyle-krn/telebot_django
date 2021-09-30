from django.shortcuts import render
from .forms import *
from .models import *
from django.http import HttpResponseRedirect

def index(request):
    product = Product.objects.all()
    return render(request, 'main_app/index.html', {'product': product})


def product_view(request):
    if request.method == "POST":
        print(request.FILES)
        product_form = ProductForm(request.POST, files=request.FILES)
        print(product_form.errors)
        if product_form.is_valid():
            product_form.save()
            return HttpResponseRedirect('/thanks/')
    else:
        product_form = ProductForm()
    return render(request, 'main_app/product.html', {'product_form': product_form})
