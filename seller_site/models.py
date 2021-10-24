from django.db import models
from django.db import models
from django.urls import reverse
from django.utils.timezone import pytz
import vape_shop.settings as settings
from django.contrib.auth.models import User


class OfflineCategory(models.Model):
    '''Модель категорий'''
    name = models.CharField(max_length=255, help_text='Имя категории')
    price_for_seller = models.DecimalField(max_digits=10, decimal_places=2, help_text='Сумма отчисления для продавца')

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

    def save(self, *args, **kwargs):
        if self.count <= 0:
            return
        if self.liquidated:
            self.product.count -= self.count
        else:
            self.product.count += self.count
        self.product.save()
        return super(OfflineReceptionProduct, self).save(*args, **kwargs)

    def get_datetime(self):
        '''Возвращает московское время'''
        user_timezone = pytz.timezone(settings.TIME_ZONE)
        datetime = self.date.astimezone(user_timezone)
        return datetime.strftime('%m/%d/%Y %H:%M')

    def get_my_model_name(self):
        return self._meta.model_name

    def __str__(self):
        return f"{self.product} -- {self.count}"



class OfflineSoldProduct(models.Model):
    '''Модель проданных товаров'''
    product = models.ForeignKey(OfflineProduct, on_delete=models.CASCADE, help_text='Продукт')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Цена на момент продажи')    
    count = models.IntegerField(help_text='Кол-во проданного товара')
    date = models.DateTimeField(auto_now_add=True, help_text='Дата и время продажи')

    def save(self, *args, **kwargs):
        if self.count <= 0:
            return
        self.product.count -= self.count
        self.product.save()
        return super(OfflineSoldProduct, self).save(*args, **kwargs)

    def get_datetime(self):
        user_timezone = pytz.timezone(settings.TIME_ZONE)
        datetime = self.date.astimezone(user_timezone)
        return datetime.strftime('%m/%d/%Y %H:%M')
    
    def get_my_model_name(self):
        return self._meta.model_name

    def __str__(self):
        return f"{self.product} -- {self.count}"


class OfflineOrderingProduct(models.Model):
    '''Модель заказа'''
    user = models.ForeignKey(User, on_delete=models.PROTECT, help_text='Продавец')
    sold_product = models.ManyToManyField(OfflineSoldProduct, help_text='Товары в заказе')  # <==== тут
    datetime = models.DateTimeField(auto_now_add=True, help_text='Дата и время создания заказа')

    def get_order_price(self):
        return sum([x.price * x.count for x in self.sold_product.all()])

    def get_datetime(self):
        user_timezone = pytz.timezone(settings.TIME_ZONE)
        datetime = self.datetime.astimezone(user_timezone)
        return datetime.strftime('%m/%d/%Y %H:%M')