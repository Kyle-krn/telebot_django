from django.urls import path, include
from .views import *
from main_app.views import RegisterUser

urlpatterns = [
    path('register_seller/', RegisterUser.as_view(), name='register'),
    path('offline_all_product/', OfflineIndexView.as_view(), name='all_product_offline'),
    path('offline_add_product/', OfflineCreateProductView.as_view(), name='add_product_offline'),
    path('offline_category/', OfflineCategoriesView.as_view(), name='category_offline'),
    path('offline_category/<int:pk>', OfflineCategoryUpdateView.as_view(), name='category_detail_offline'),
    path('offline_subcategory/<int:pk>', OfflineCategoryUpdateView.as_view(model=OfflineSubCategory,
                                                                           form_class = OfflineSubcategoryForm,
                                                                           success_message = 'Подкатегория успешно обновлена!'), name='subcategory_detail_offline'),
    path('offline_product/<int:pk>', OfflineProductAdminView.as_view(), name='product_detail_offline'),

    path('offline_order/', make_order_view, name='order_offline'),
    path('offline_reception/', reception_view, name='reception_offline'),
    path('offline_list_order/', OfflineOrderView.as_view(), name='list_order_offline'),
    path('offline_stat/', OfflineStatisticView.as_view(), name='stat_offline'),
    path('offline_my_sales', OfflineSellerPage.as_view(), name='my_sales_offline')

]