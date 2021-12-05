from django.db import models
from main_app.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import pytz
from django.conf import settings

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    author = models.CharField(max_length=50)
    rating = models.IntegerField(
    validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ('-created',)



ORDER_STATUS = [
    ('Created', 'Созданно'),
    ('Processing', 'В процессе'),
    ('Shipped', 'Доставляется'),
    ('Ready for pickup', 'Ожидает получения'),
    ('Completed', 'Доставленно')
    ]



class SoldSiteProduct(models.Model):
    '''Проданные товары через сайт'''
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text='Продукт')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Цена на момент продажи')    
    count = models.IntegerField(help_text='Кол-во проданного товара')
    date = models.DateTimeField(auto_now_add=True, help_text='Дата и время продажи')
    order = models.ForeignKey('OrderSiteProduct', related_name='soldproduct', on_delete=models.CASCADE, help_text='Заказ')

    # def save(self, *args, **kwargs):
    #     '''Отнимает кол-во товара в OfflineProduct'''
    #     if self.count <= 0:
    #         return
    #     self.product.count -= self.count
    #     self.product.save()
    #     return super(SoldSiteProduct, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.product.title} - {self.count} в заказе #{self.order.pk}"


class OrderSiteProduct(models.Model):
    '''Заказы через сайт, пока не используется в приложении'''
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    note = models.TextField(blank=True)
    transport_cost = models.DecimalField(max_digits=10, decimal_places=2)
    track_code = models.CharField(max_length=100, blank=True, null=True, help_text='Трек-код заказа')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='Created')
    price = models.IntegerField(blank=True, null=True)

    def set_order_price(self):
        '''Обновляет стоймость заказа при его изменении'''
        self.price = sum([x.price * x.count for x in self.soldproduct.all()])
        return self.save()

    def get_datetime(self):
        user_timezone = pytz.timezone(settings.TIME_ZONE)
        datetime = self.created.astimezone(user_timezone)
        return datetime.strftime('%m/%d/%Y %H:%M')

    def __str__(self) -> str:
        return f'Заказ #{self.id}'