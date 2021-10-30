from django.urls import path
from .views import *
from django.conf.urls.static import static
from vape_shop import settings
from .models import *
from .forms import *

urlpatterns = [
    path('', IndexView.as_view(), name='all_product'),                                                                          # Все товары
    path('product/<int:pk>', ProductView.as_view(), name='productdetail'),                                                      # Товар - подробнее
    path('category/<int:pk>', CategoryUpdateView.as_view(), name='category_detail'),                                            # Катеогрии - подробнее
    path('subcategory/<int:pk>', CategoryUpdateView.as_view(model=SubCategory, 
                                                            form_class=Subcategory_reqForm,
                                                            success_message = 'Подкатегория успешно обновлена!'), name='subcategory_detail'),        # Подкатеогии - подробнее
    path('add_category/', CategoriesView.as_view(), name='add_category'),                                                       # Новая катеогрия
    path('add_product/', CreateProductView.as_view(), name='add_product'),                                                      # Новый товар
    path('user_stat/', StatisticView.as_view(), name='user_stat'),                                                              # Общая статистика
    path('reception/', ReceptionProductView.as_view(), name='reception'),                                                       # Приемка товара
    path('new_order/', NoPaidOrderView.as_view(), name='new_order'),                                                            # Неоплаченные заказы
    path('old_order/', PaidOrderView.as_view(), name='old_order'),                                                               # Оплаченные заказы
    path('qiwi_order/', QiwiOrderView.as_view(), name='qiwi_order'),                                                               # Оплаченные заказы
    path('qiwi/', control_qiwi, name='qiwi'),                                       # Добавить, удалить токен для QIWI    
    ]


