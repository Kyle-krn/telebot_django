"""vape_shop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from vape_shop import settings
from main_app.views import LoginUser, logout_user, index
import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('main/', include('main_app.urls', namespace='admin_panel')),
    path('login/', LoginUser.as_view(), name='login'),                                                                          # Логин
    path('logout/', logout_user, name='logout'),                                                                                # Разлогиниться
    path('', index, name='index_url'),                                                                                # Разлогиниться
    path('seller/', include('seller_site.urls', namespace='local_shop')),
    # path('', include('online_shop.urls', namespace='online_shop')),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)