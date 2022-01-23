from django.urls import path
from .views import *

app_name = 'online_shop'

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    # path('order/create', order_create, name='order_create'),
    path('order/create', CreateOrderView.as_view(), name='order_create'),
    path('order/<int:order_id>/pdf/', invoice_pdf, name='invoice_pdf'),
    path('product/<slug:slug>', ProductDetailView.as_view(), name='product_detail'),
    path('<slug:category_slug>', ProductListView.as_view(), name='product_list_by_category'),
    path('<slug:category_slug>/<slug:subcategory_slug>', ProductListView.as_view(), name='product_list_by_subcategory'),
    path('validate/', validate_postal_code, name='validate_postal_code'),
    

]
