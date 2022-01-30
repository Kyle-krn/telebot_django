
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from vape_shop import settings
from main_app.views import index
import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('main/', include('main_app.urls', namespace='admin_panel')),                                                                     
    path('accounts/', include('accounts.urls'), name='index_url'),                                                   
    path('seller/', include('seller_site.urls', namespace='local_shop')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('', include('online_shop.urls', namespace='online_shop')),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)