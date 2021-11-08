from django.shortcuts import render, get_object_or_404, redirect, get_object_or_404
from .forms import *
from .models import *
from django.http import HttpResponseRedirect
from django.contrib import messages
from itertools import chain
from django.db.models import Q, query
from main_app.management.commands.utils import get_qiwi_balance
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView
from django.views import View
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import login 
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return redirect('all_product') if request.user.is_superuser else redirect('local_shop:list_product')


class LoginUser(LoginView):
    '''Аутенификация пользователя'''
    form_class = LoginUserForm
    template_name = 'main_app/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Логин'
        return context

    def form_valid(self, form):
        login(self.request, form.get_user())
        user = form.get_user()
        return HttpResponseRedirect(self.get_success_url(user))

    def get_success_url(self, user):
        if user.is_superuser:
            return reverse_lazy('all_product')
        else:
            return reverse_lazy('local_shop:list_product')

def logout_user(request):
    '''Выход'''
    logout(request)
    return redirect('login')


@method_decorator(staff_member_required, name='dispatch')
class IndexView(LoginRequiredMixin, ListView):
    '''Вывод всех товаров'''
    context_object_name = 'product'
    login_url = '/login/'
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


    def post(self, request):
        form = ProductDeleteForm(request.POST)
        if form.is_valid():
            cf = form.cleaned_data
            Product.objects.get(pk=cf['id']).delete()
        return redirect('all_product')


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Все товары'
        context['category'] = Category.objects.all()
        context['delete_form'] = ProductDeleteForm()
        return context

@method_decorator(staff_member_required, name='dispatch')
class CreateProductView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    '''Создание нового товара'''
    template_name = 'main_app/add_product.html'
    form_class = ProductForm
    success_message = "Товар успешно создан!"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Новый товар'
        context['category'] = Category.objects.all()
        return context


@method_decorator(staff_member_required, name='dispatch')
class ReceptionProductView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    '''Представление добавления кол-ва товара (приемка)'''
    template_name = 'main_app/reception.html'
    form_class = ReceptionForm
    success_url = reverse_lazy('reception')
    success_message = 'Количество товара успешно увеличено!'


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Приемка товара'
        context['category'] = Category.objects.all()
        return context


@method_decorator(staff_member_required, name='dispatch')
class CategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    '''Обновить категорию'''
    model = Category
    template_name = 'main_app/category_detail.html'
    form_class = Category_reqForm
    success_url = reverse_lazy('add_category')
    success_message = 'Категория успешно обновлена!'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Изменить категорию/подкатегорию'
        return context

    def post(self, *args, **kwargs):
        if 'delete' in self.request.POST:
            category = self.get_object()
            category.delete()
            return redirect('add_category')
        return super().post(self)


@method_decorator(staff_member_required, name='dispatch')
class CategoriesView(LoginRequiredMixin, View):
    '''Представление создания/просмотра категорий/подкатегорий'''
    template_name = 'main_app/category.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['title'] = 'Категории (Онлайн магазин)'
        context['queryset'] = Category.objects.all()
        context['category_form'] = CategoryForm()
        context['sc_form'] = SubcategoryForm()
        return context

    def post(self, request):
        if 'create_category' in request.POST:   # Создать категорию
            category_form = CategoryForm(request.POST, files=request.FILES)
            if category_form.is_valid():
                category_form.save()
                messages.success(request, 'Новая категория успешно создана!')
                return redirect('add_category')

        elif 'create_sc' in request.POST:   # Создать подкатеогрию
            sc_form = SubcategoryForm(request.POST, files=request.FILES)
            print(sc_form.is_valid())
            print(sc_form.errors)
            # if sc_form.is_valid():
            #     if 'category_id' not in request.POST:
            #         return redirect('all_product')

            #     try:
            #         pk = int(request.POST['category_id'])
            #     except (ValueError, TypeError):
            #         messages.error(request, 'Ошибка создания подкатегории!')
            #         return redirect('all_product')

            #     f = sc_form.save(commit=False)
            #     f.category = get_object_or_404(Category, pk=pk)
            #     f.save()
            #     messages.success(request, 'Новая подкатегория успешно создана!')
            return redirect('add_category')

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data())


class QiwiOrderView(LoginRequiredMixin, ListView):
    template_name = 'main_app/order.html'
    queryset = OrderingProduct.objects.filter(qiwi_bool=True).order_by('-datetime')
    context_object_name = 'queryset'

    def post(self, request):
        if 'order_id' not in request.POST and 'track_code' not in request.POST:
            messages.error(request, 'Ошибка добавления трек-кода!')
            return redirect('all_product')

        try:
            order_id = int(request.POST['order_id'])
            track_code = request.POST['track_code']
        except (ValueError, TypeError):
            messages.error(request, 'Ошибка добавления трек-кода!')
            return redirect('all_product')

        order = get_object_or_404(OrderingProduct, pk=order_id)
        # order = OrderingProduct.objects.get(pk=order_id)
        order.track_code = track_code
        order.save()
        messages.success(request, 'Трек-номер успешно добавлен!')
        return redirect('qiwi_order')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'QIWI заказы'
        return context


class SiteOrderView(LoginRequiredMixin, ListView):
    template_name = 'main_app/site_order.html'
    queryset = OrderSiteProduct.objects.all().order_by('-created')
    context_object_name = 'queryset'

    def post(self, request):
        if 'order_id' not in request.POST and 'track_code' not in request.POST:
            messages.error(request, 'Ошибка добавления трек-кода!')
            return redirect('all_product')

        try:
            order_id = int(request.POST['order_id'])
            track_code = request.POST['track_code']
        except (ValueError, TypeError):
            messages.error(request, 'Ошибка добавления трек-кода!')
            return redirect('all_product')

        order = get_object_or_404(OrderingProduct, pk=order_id)
        # order = OrderingProduct.objects.get(pk=order_id)
        order.track_code = track_code
        order.save()
        messages.success(request, 'Трек-номер успешно добавлен!')
        return redirect('qiwi_order')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'QIWI заказы'
        return context

    

@method_decorator(staff_member_required, name='dispatch')
class NoPaidOrderView(LoginRequiredMixin, ListView):
    '''Неоплаченные заказы'''
    template_name = 'main_app/manager_order.html'
    queryset = OrderingProduct.objects.filter(Q(payment_bool=False) & Q(qiwi_bool=False)).order_by('-datetime')
    context_object_name = 'queryset'
    

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Неоплаченные заказы'
        return context

    def post(self, request):
        if 'paid_status' in request.POST:
            if 'order_id' not in request.POST:
                messages.error(request, 'Ошибка изменения статуса заказа!')
                return redirect('all_product')

            try:
                order_id = int(request.POST['order_id'])
            except (ValueError, TypeError):
                messages.error(request, 'Ошибка изменения статуса заказа!')
                return redirect('all_product')

            order = get_object_or_404(OrderingProduct, pk=order_id)
            # order = OrderingProduct.objects.get(pk=order_id)
            if request.POST['payment'] == 'paid':        
                for item in order.sold_product.all():
                    item.product.count -= item.count
                    item.product.save()
                    item.payment_bool = True
                    item.save()
                order.payment_bool = True
                order.save()
                messages.success(request, 'Заказ успешно обработан!')
            else:
                order.sold_product.all().delete()
                order.delete()
                messages.success(request, 'Заказ успешно удален!')

        elif 'change_order' in request.POST:
            if 'product_id' not in request.POST and 'product_count' not in request.POST:
                messages.error(request, 'Ошибка изменения заказа!')
                return redirect('all_product')
            list_id = request.POST.getlist('product_id')
            list_count = request.POST.getlist('product_count')

            if len(list_count) != len(list_id):
                messages.error(request, 'Ошибка изменения заказа!')
                return redirect('all_product')

            try:
                tuple_product = [(int(list_id[i]), int(list_count[i])) for i in range(len(list_id))]
            except (ValueError, TypeError):
                messages.error(request, 'Ошибка изменения заказа!')
                return redirect('all_product')

            for item in tuple_product:
                if item[1] <= 0:
                    sold_product = get_object_or_404(SoldProduct, pk=item[0])
                    sold_product.delete()
                    # SoldProduct.objects.get(pk=item[0]).delete()
                else:
                    SoldProduct.objects.filter(pk=item[0]).update(count=item[1])

            messages.success(request, 'Заказ успешно изменен!')
        return redirect('new_order')



@method_decorator(staff_member_required, name='dispatch')
class PaidOrderView(LoginRequiredMixin, ListView):
    '''Оплаченные заказы'''
    template_name = 'main_app/manager_order.html'
    queryset = OrderingProduct.objects.filter(Q(payment_bool=True) & Q(qiwi_bool=False)).order_by('-datetime')
    context_object_name = 'queryset'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Оплаченные заказы'
        return context

    def post(self, request):
        if 'order_id' not in request.POST and 'track_code' not in request.POST:
            messages.error(request, 'Ошибка добавления трек-кода!')
            return redirect('all_product')

        try:
            order_id = int(request.POST['order_id'])
            track_code = request.POST['track_code']
        except (ValueError, TypeError):
            messages.error(request, 'Ошибка добавления трек-кода!')
            return redirect('all_product')

        order = get_object_or_404(OrderingProduct, pk=order_id)
        # order = OrderingProduct.objects.get(pk=order_id)
        order.track_code = track_code
        order.save()
        messages.success(request, 'Трек-номер успешно добавлен!')
        return redirect('old_order')

@method_decorator(staff_member_required, name='dispatch')
class StatisticView(LoginRequiredMixin, View):
    '''Представления общей статистики по товарам'''
    template_name = 'main_app/user_stat.html'
    # sold_queryset = SoldProduct.objects.filter(payment_bool=True)
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
        self.sold_queryset = SoldProduct.objects.filter(payment_bool=True)
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
        # if 'start' in self.get_params() or 'end' in self.get_params():
        self.get_queryset()
        return render(request, self.template_name, context=self.get_context_data())

@method_decorator(staff_member_required, name='dispatch')
class ProductView(LoginRequiredMixin, View):
    '''Детальное представление товара и управление им'''
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
        context['title'] = self.product.title
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
                messages.success(request, 'Товар успешно обновлен!')
                return redirect('productdetail', pk=pk)

        elif 'delete' in request.POST:
            self.product.delete()
            messages.success(request, 'Товар усппешно удален!')
            return redirect ('all_product')

        elif 'reception' in request.POST:
            form = ReceptionForm(request.POST)
            if form.is_valid():
                self.product.count += form.cleaned_data['count']
                self.product.save()
                f = form.save(commit=False)
                f.product = self.product
                f.save()
                messages.success(request, 'Количество товара успешно увеличено!')
                return redirect('productdetail', pk=pk)           

        elif 'liquidated' in request.POST:
            form = ReceptionForm(request.POST)
            if form.is_valid():
                self.product.count -= form.cleaned_data['count']
                self.product.save()
                f = form.save(commit=False)
                f.product = self.product
                f.liquidated = True
                f.save()
                messages.success(request, 'Товар успешно списан!')
                return redirect('productdetail', pk=pk)
        

    def get(self, request, pk):
        self.get_object()
        self.get_queryset(pk)
        return render(request, self.template_name, context=self.get_context_data())



def control_qiwi(request):
    '''Для оплаты Qiwi . В приложении не используется'''
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
            messages.success(request, 'Ошибка получения баланса кошелька')
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
