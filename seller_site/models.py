from django.db import models
from django.db import models
from django.urls import reverse
from django.utils.timezone import pytz
import vape_shop.settings as settings

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
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Цена товара')
    count = models.IntegerField(default=0, help_text='Остаток на складе')
    subcategory = models.ForeignKey(OfflineSubCategory, on_delete=models.CASCADE, help_text='Подкатегория товара')

    # def get_absolute_url(self):
    #     return reverse('productdetail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title
