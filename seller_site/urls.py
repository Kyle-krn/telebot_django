from django.urls import path, include
from .views import *

urlpatterns = [
    path('', OfflineIndexView.as_view(), name='all_product_offline'),
    path('register_seller/', RegisterUser.as_view(), name='register'),
    path('add_product/', OfflineCreateProductView.as_view(), name='add_product_offline'),
    path('category/', OfflineCategoriesView.as_view(), name='category_offline'),
    path('product/<int:pk>', OfflineProductAdminView.as_view(), name='product_detail_offline'),
    path('order/', make_order_view, name='order_offline'),
    path('reception/', reception_view, name='reception_offline'),
    path('list_order/', OfflineOrderView.as_view(), name='list_order_offline'),
    path('stat/', OfflineStatisticView.as_view(), name='stat_offline'),
    path('my_sales', OfflineSellerPage.as_view(), name='my_sales_offline')

]