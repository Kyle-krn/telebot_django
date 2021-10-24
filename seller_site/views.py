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

def make_order_view(request):
    print('here')
    if request.method == 'POST':
        pk_list = request.POST.getlist('product_id')
        count_list = request.POST.getlist('product_count')
        l_list = [(pk_list[i], count_list[i]) for i in range(len(pk_list))]
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def reception_view(request):
    if request.method == 'POST':
        print(request.POST)
        count =int(request.POST.get('count_reception'))
        note = request.POST.get('note_reception')
        product_pk = int(request.POST.get('product_id'))
        product = OfflineProduct.objects.get(pk=product_pk)
        OfflineReceptionProduct.objects.create(product=product, user=request.user, note=note, price=product.purchase_price, count=count)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


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
            category_pk = int(request.POST.get('category_pk'))
            name = request.POST.get('category_name')
            category = OfflineCategory.objects.get(pk=category_pk)  # Изменить на update
            category.name = name                                    #   
            category.save()                                         #
            messages.info(request, 'Категория  успешно изменена!')

        elif 'delete_category' in request.POST:
            category_pk = int(request.POST.get('category_pk'))
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
            subcategory_pk = int(request.POST.get('subcategory_pk'))
            subcategory_name = request.POST.get('subcategory_name')
            subcategory = OfflineSubCategory.objects.get(pk=subcategory_pk) # Изменить на update
            subcategory.name = subcategory_name
            subcategory.save()
            messages.info(request, 'Подкатегория успешно изменена!')

        elif 'delete_subcategory' in request.POST:
            subcategory_pk = int(request.POST.get('subcategory_pk'))
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
            pk_product = int(request.POST.get('pk_p'))
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
        print(self.product)

    def get_params(self):
        return {k:v for k,v in self.request.GET.items() if v != ''}

    def get_context_data(self, **kwargs):
        context = {}
        context['product'] = self.product
        context['title'] = self.product.title
        context['category'] = OfflineCategory.objects.all()
        context['reception_form'] = OfflineReceptionForm()
        context['product_form'] = OfflineProductForm(initial={'title': self.product.title,
                                        'price': self.product.price,
                                        'purchase_price': self.product.purchase_price,
                                        'subcategory': self.product.subcategory_id})
        return context

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
        # self.get_queryset(pk)
        return render(request, self.template_name, context=self.get_context_data())