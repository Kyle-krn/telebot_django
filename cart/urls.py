from django.urls import path
from .views import *

app_name = 'cart'

urlpatterns = [
    path('cart/', CartDetailView.as_view(), name='cart_detail'),            # Детальное представление корзины
    path('cart/add/<int:product_id>', cart_add, name='cart_add'),           # Добавить товар в корзину
    path('cart/remove/<int:product_id>', cart_remove, name='cart_remove'),  # Убрать товар из корзины
]