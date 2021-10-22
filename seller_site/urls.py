from django.urls import path, include
from .views import *

urlpatterns = [
    path('', main_seller_view, name='seller_main'),

]