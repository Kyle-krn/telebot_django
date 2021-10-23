from django.db import models
from django.db import models
from django.urls import reverse
from django.utils.timezone import pytz
import vape_shop.settings as settings
from django.contrib.auth.models import User


class OfflineCategory(models.Model):
    '''Модель категорий'''
    name = models.CharField(max_length=255, help_text='Имя категории')

    def __str__(self):
        return self.name


class OfflineSubCategory(models.Model):
    '''Модель подкатегорий'''
    category = models.ForeignKey(OfflineCategory, on_delete=models.CASCADE, help_text='Категория подкатегории')
    name = models.CharField(max_length=150, db_index=True, help_text='Имя подкатегории')


    def __str__(self):
        return self.name


class OfflineProduct(models.Model):
    '''Модель товара'''
    title = models.CharField(max_length=255, verbose_name='Название товара')
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Закупочная цена товара')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Цена товара')
    count = models.IntegerField(default=0, help_text='Остаток на складе')
    subcategory = models.ForeignKey(OfflineSubCategory, on_delete=models.CASCADE, help_text='Подкатегория товара')

    def get_absolute_url(self):
        return reverse('product_detail_offline', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title


class OfflineReceptionProduct(models.Model):
    '''Модель пополнения кол-ва товара (приемка)'''
    product = models.ForeignKey(OfflineProduct, on_delete=models.CASCADE, help_text='Товар')
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    note = models.CharField(max_length=255, blank=True, null=True, help_text='Заметка приемки')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Закупочная цена')
    count = models.IntegerField(help_text='Кол-во товара в приемке')
    date = models.DateTimeField(auto_now_add=True, help_text='Дата и время приемки')
    liquidated = models.BooleanField(default=False, help_text='Ликвидация товара') # True для ликвидированного товара

    def get_datetime(self):
        '''Возвращает московское время'''
        user_timezone = pytz.timezone(settings.TIME_ZONE)
        datetime = self.date.astimezone(user_timezone)
        return datetime.strftime('%m/%d/%Y %H:%M')

    def get_my_model_name(self):
        return self._meta.model_name

    def __str__(self):
        return f"{self.product} -- {self.count}"
