from django.urls import path, include
from .views import *

app_name = 'local_shop'

urlpatterns = [
    path('', OfflineIndexView.as_view(), name='list_product'),
    path('register_seller/', RegisterUser.as_view(), name='register_seller'),
    path('add_product/', OfflineCreateProductView.as_view(), name='create_product'),
    path('category/', OfflineCategoriesView.as_view(), name='list_category'),
    path('product/<int:pk>', OfflineProductAdminView.as_view(), name='product_detail'),
    path('make_order/', CreateOrderView.as_view(), name='create_order'),
    path('reception/', OfflineReceptionProductView.as_view(), name='create_reception'),
    path('list_order/', OfflineOrderView.as_view(), name='list_order'),
    path('stat/', OfflineStatisticView.as_view(), name='statistic'),
    path('my_sales', OfflineSellerPage.as_view(), name='my_sales'),

    path('change_order/<int:sold_pk>', change_item_order, name='change_order'),
    path('remove_item_in_order/<int:sold_pk>', remove_item_order, name='remove_item_in_order'),
    path('delete_order/<int:order_pk>', delete_order, name='delete_order')
]