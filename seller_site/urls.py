from django.urls import path, include
from .views import *
from main_app.views import RegisterUser

urlpatterns = [
    path('', main_seller_view, name='seller_main'),
    path('register_seller/', RegisterUser.as_view(), name='register'),
    path('offline_all_product/', OfflineIndexView.as_view(), name='all_product_offline'),
    path('offline_add_product/', OfflineCreateProductView.as_view(), name='add_product_offline'),
    path('offline_category/', OfflineCategoriesView.as_view(), name='category_offline'),
    path('offline_category/<int:pk>', OfflineCategoryUpdateView.as_view(), name='category_detail_offline'),
    path('offline_subcategory/<int:pk>', OfflineCategoryUpdateView.as_view(model=OfflineSubCategory,
                                                                           form_class = OfflineSubcategoryForm,
                                                                           success_message = 'Подкатегория успешно обновлена!'), name='subcategory_detail_offline'),
]