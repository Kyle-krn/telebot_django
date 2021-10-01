from django.urls import path, re_path
from .views import *
from django.conf.urls.static import static
from vape_shop import settings


urlpatterns = [
    path('', index, name='all_product'),
    path('product/<int:pk>', product_view, name='productdetail'),
    path('category/<int:pk>', category_view, name='category_detail'),
    path('add_category/', create_category, name='add_category'),
    ]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)