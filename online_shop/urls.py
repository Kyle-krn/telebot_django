from django.urls import path, include
from .views import *

app_name = 'online_shop'

urlpatterns = [
    
    path('', product_list, name='product_list'),
    path('cart/', cart_detail, name='cart_detail'),
    path('order/create', order_create, name='order_create'),
    path('<slug:subcategory_slug>', product_list, name='product_list_by_category'),
    path('<slug:subcategory_slug>/<slug:product_slug>', product_detail, name='product_detail'),
    
    path('cart/add/<int:product_id>', cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>', cart_remove, name='cart_remove'),
    

    path('validate/', validate_postal_code, name='validate_postal_code')

]