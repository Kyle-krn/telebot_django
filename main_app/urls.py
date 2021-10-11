from django.urls import path, re_path
from .views import *
from django.conf.urls.static import static
from vape_shop import settings


urlpatterns = [
    path('', IndexView.as_view(), name='all_product'),                              # Все товары
    path('product/<int:pk>', product_view, name='productdetail'),                   # Товар - подробнее
    path('category/<int:pk>', category_view, name='category_detail'),               # Катеогрии - подробнее
    path('subcategory/<int:pk>', subcategory_view, name='subcategory_detail'),      # Подкатеогии - подробнее
    path('add_category/', create_category, name='add_category'),                    # Новая катеогрия
    path('add_product/', CreateProductView.as_view(), name='add_product'),          # Новый товар
    path('new_order/', new_order, name='new_order'),                                # Необработанные заказы
    path('old_order/', old_order, name='old_order'),                                # Обработанные заказы
    path('qiwi/', control_qiwi, name='qiwi'),                                       # Добавить, удалить токен для QIWI
    path('user_stat/', user_stat, name='user_stat'),                                # Общая статистика
    # path('reception/<int:pk>', reception_product, name='reception'),              
    path('login/', LoginUser.as_view(), name='login'),                              # Логин
    path('logout/', logout_user, name='logout'),                                    # Разлогиниться
    path('reception/', reception_product, name='reception'),                        # Приемка товара
    ]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)