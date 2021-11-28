from django.urls import path
from .views import *
from django.conf.urls.static import static
from vape_shop import settings
from .models import *
from .forms import *

app_name = 'admin_panel'

urlpatterns = [
    path('', IndexView.as_view(), name='list_product'),                                                                                     # Все товары   
    path('product/<int:pk>', ProductView.as_view(), name='productdetail'),                                                                  # Товар - подробнее
    path('category/<int:pk>', CategoryUpdateView.as_view(), name='categorydetail'),                                                         # Катеогрии - подробнее
    path('subcategory/<int:pk>', CategoryUpdateView.as_view(model=SubCategory, 
                                                            form_class=Subcategory_reqForm,
                                                            success_message = 'Подкатегория успешно обновлена!'), name='subcategorydetail'),# Подкатеогии - подробнее
    path('create_category/', CategoriesView.as_view(), name='create_category'),                                                             # Создать катеогрию
    path('create_product/', CreateProductView.as_view(), name='create_product'),                                                            # Создать товар
    path('statistic/', StatisticView.as_view(), name='statistic'),                                                                          # Общая статистика
    path('reception/', ReceptionProductView.as_view(), name='reception'),                                                                   # Приемка товара
    path('new_order/', NoPaidOrderView.as_view(), name='no_paid_order'),                                                                    # Неоплаченные заказы
    path('old_order/', PaidOrderView.as_view(), name='paid_order'),                                                                         # Оплаченные заказы
    path('qiwi_order/', QiwiOrderView.as_view(), name='qiwi_order'),                                                                        # Заказы через Qiwi


    path('site_new_order/', SiteOrderView.as_view(), name='site_new_order'),                                                                 

    path('qiwi/', ControlQiwiView.as_view(), name='control_qiwi'),                                                                          # Добавить, удалить токен для QIWI    

    path('change_item_order/<int:sold_pk>', change_item_order, name='change_item_order'),                                                   # Изменить кол-во товара в неоплаченном заказе
    path('delete_order/<int:order_pk>', delete_order, name='delete_order'),                                                                 # Удалить заказ  
    path('remove_item_order/<int:sold_pk>', remove_item_order, name='remove_item_order'),                                                   # Удалить товар из заказа
    path('add_track_code_in_order/<int:order_pk>', add_track_code_in_order, name='add_track_code_in_order'),                                # Добавить трек код
    ]

