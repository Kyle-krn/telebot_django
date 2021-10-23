from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .models import *
from django.contrib import messages
from .forms import *
from django.views.generic.edit import UpdateView, CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import ListView


def main_seller_view(request):
    return render(request, 'seller_site/base.html')


class OfflineCategoriesView(LoginRequiredMixin, View):
    '''Представление создания/просмотра категорий/подкатегорий'''
    template_name = 'seller_site/offline_category.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['title'] = 'Категории (Оффлайн магазин)'
        context['queryset'] = OfflineCategory.objects.all()
        context['category_form'] = OffilneCategoryForm()
        context['sc_form'] = OfflineSubcategoryForm()
        return context

    def post(self, request):
        if 'create_category' in request.POST:   # Создать категорию
            category_form = OffilneCategoryForm(request.POST)
            if category_form.is_valid():
                category_form.save()
                messages.info(request, 'Новая категория успешно создана!')
                return redirect('category_offline')
        elif 'create_sc' in request.POST:   # Создать подкатеогрию
            sc_form = OfflineSubcategoryForm(request.POST)
            if sc_form.is_valid():
                f = sc_form.save(commit=False)    
                f.category = OfflineCategory.objects.get(pk=int(request.POST['category_id']))
                f.save()
                messages.info(request, 'Новая подкатегория успешно создана!')
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

