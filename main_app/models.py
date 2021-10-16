from django.db import models
from django.contrib.auth.models import User
# from django.utils.text import slugify
from slugify import slugify
from django.urls import reverse
from django.utils.timezone import pytz
import vape_shop.settings as settings

class Category(models.Model):
    '''Модель категорий'''
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='category_img/')
    slug = models.CharField(max_length=255, unique=True, blank=True, null=True)
    max_count_product = models.IntegerField()

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        self.slug = f'c||{self.pk}'
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    '''Модель подкатегорий'''
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, db_index=True)
    photo = models.ImageField(upload_to='subcategory_img/')
    slug = models.CharField(max_length=255, unique=True, blank=True, null=True)


    def save(self, *args, **kwargs):
        super(SubCategory, self).save(*args, **kwargs)
        self.slug = f'sc||{self.pk}'
        super(SubCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    '''Модель товара'''
    title = models.CharField(max_length=255, verbose_name='Название товара')
    photo = models.ImageField(upload_to='product_img/')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.IntegerField(default=0)
    slug = models.CharField(max_length=255, unique=True, blank=True, null=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    weight = models.IntegerField()

    def save(self, *args, **kwargs):
        super(Product, self).save(*args, **kwargs)
        self.slug = f'p||{self.pk}' # Короткий слаг из id для индентификации товара в боте
        super(Product, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('productdetail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title


class ReceptionProduct(models.Model):
    '''Модель пополнения кол-ва товара (приемка)'''
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    note = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    liquidated = models.BooleanField(default=False) # True для ликвидированного товара

    def get_datetime(self):
        user_timezone = pytz.timezone(settings.TIME_ZONE)
        datetime = self.date.astimezone(user_timezone)
        return datetime.strftime('%m/%d/%Y %H:%M')

    def get_my_model_name(self):
        return self._meta.model_name

    def __str__(self):
        return f"{self.product} -- {self.count}"


class TelegramUser(models.Model):
    '''Модель юзеров из телеграма'''
    chat_id = models.IntegerField(unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    fio = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    number = models.BigIntegerField(blank=True, null=True)
    post_index = models.IntegerField(blank=True, null=True)
    search_data = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.chat_id} -- {self.username}"


class TelegramProductCartCounter(models.Model):
    '''Модель для каунтера, используется для клавиатуры добавления в корзину'''
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)
    counter = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} -- {self.count}"


class PayProduct(models.Model):
    '''Модель бронирования товара на оплату -  используется для оплаты через qiwi'''
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    product_pay = models.IntegerField()
    pay_comment = models.CharField(max_length=255)
    delivery_pay = models.IntegerField()
    datetime = models.DateTimeField(auto_now_add=True)


class QiwiToken(models.Model):
    '''Модель для QIWI токена'''
    number = models.BigIntegerField(blank=True, null=True)
    balance = models.IntegerField(blank=True, null=True)
    token = models.CharField(max_length=255)
    active = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)


###########################################################################
class SoldProduct(models.Model):
    '''Модель проданных товаров'''
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)    
    count = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    payment_bool = models.BooleanField(default=False)

    def get_datetime(self):
        user_timezone = pytz.timezone(settings.TIME_ZONE)
        datetime = self.date.astimezone(user_timezone)
        return datetime.strftime('%m/%d/%Y %H:%M')
    
    def get_my_model_name(self):
        return self._meta.model_name

    def __str__(self):
        return f"{self.product} -- {self.count}"


class OrderingProduct(models.Model):
    '''Модель заказа'''
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    delivery_pay = models.IntegerField()
    sold_product = models.ManyToManyField(SoldProduct)  # <==== тут
    track_code = models.BigIntegerField(blank=True, null=True)
    check_admin = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True)
    fio = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    number = models.BigIntegerField(blank=True, null=True)
    post_index = models.BigIntegerField(blank=True, null=True)
    payment_bool = models.BooleanField(default=False)


    def get_order_price(self):
        return sum([x.count * x.price for x in self.sold_product.all()]) + self.delivery_pay

    def get_datetime(self):
        user_timezone = pytz.timezone(settings.TIME_ZONE)
        datetime = self.datetime.astimezone(user_timezone)
        return datetime.strftime('%m/%d/%Y %H:%M')

###########################################################################
