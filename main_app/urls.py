from django.urls import path, re_path
from .views import *
from django.conf.urls.static import static
from vape_shop import settings


urlpatterns = [
    path('', index, name='all_product'),
    path('product/<int:pk>', product_view, name='productdetail'),
    path('category/<int:pk>', category_view, name='category_detail'),
    path('subcategory/<int:pk>', subcategory_view, name='subcategory_detail'),
    path('add_category/', create_category, name='add_category'),
    path('add_product/', create_product, name='add_product'),
    path('new_order/', new_order, name='new_order'),
    path('old_order/', old_order, name='old_order'),
    path('qiwi/', control_qiwi, name='qiwi'),
    path('user_stat/', user_stat, name='user_stat'),
    path('reception/<int:pk>', reception_product, name='reception'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    ]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)