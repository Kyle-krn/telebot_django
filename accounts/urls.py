from django.contrib.auth import views as auth_views
from django.urls import path
from .views import *

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),                                                                   # Представление логина
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),                                      # Смена пароля
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),                        # Пароль изменен
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),                                         # Сборосить пароль
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),                           # Успешный сброс пароля
    path('password_reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),          # Подтверждение сброса пароля
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),               # Пароль сброшен
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),                                                                # Разлогиниться   
    path('register/', RegisterUser.as_view(), name='register'),                                                                     # Регистрация
    path('profile/', ProfileView.as_view(), name='profile')                                                                         # Профиль
    ]