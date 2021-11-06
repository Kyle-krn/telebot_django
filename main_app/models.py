from django.db import models
from django.urls import reverse
from django.utils.timezone import pytz
import vape_shop.settings as settings
from pytils.translit import slugify

class Category(models.Model):
    '''Модель категорий'''
    name = models.CharField(max_length=255, help_text='Имя категории')
    photo = models.ImageField(upload_to='category_img/', help_text='Фото категории')
    slug = models.SlugField(max_length=100, unique=True)
    pk_for_telegram = models.CharField(max_length=255, unique=True, blank=True, null=True, help_text='Используется в боте для поиска категории')
    max_count_product = models.IntegerField()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)
        self.pk_for_telegram = f'c||{self.pk}' # Слаг id из за ограничений телеграма в callback_data
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    '''Модель подкатегорий'''
    category = models.ForeignKey(Category, on_delete=models.CASCADE, help_text='Категория подкатегории')
    name = models.CharField(max_length=150, db_index=True, help_text='Имя подкатегории')
    photo = models.ImageField(upload_to='subcategory_img/', help_text='Фотоподкатегории')
    slug = models.SlugField(max_length=100, unique=True)
    pk_for_telegram = models.CharField(max_length=255, unique=True, blank=True, null=True, help_text='Используется в боте для поиска категории')

    def get_absolute_url(self):
        return reverse('online_shop:product_list_by_category', kwargs={'subcategory_slug': self.slug})


    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(SubCategory, self).save(*args, **kwargs)
        self.pk_for_telegram = f'sc||{self.pk}'
        super(SubCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    '''Модель товара'''
    title = models.CharField(max_length=255, verbose_name='Название товара')
    photo = models.ImageField(upload_to='product_img/', help_text='Фото товара')
    description = models.TextField(help_text='Описание товара')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Цена товара')
    count = models.IntegerField(default=0, help_text='Остаток на складе')
    slug = models.SlugField(max_length=100, unique=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, help_text='Подкатегория товара')
    weight = models.IntegerField(help_text='Вес товара')
    pk_for_telegram = models.CharField(max_length=255, unique=True, blank=True, null=True, help_text='Используется в боте для поиска категории')

    def get_average_review_score(self):
        average_score = 0.0
        if self.reviews.count() > 0:
            total_score = sum([review.rating for review in self.reviews.all()])
            average_score = total_score / self.reviews.count()
            return round(average_score, 1)


    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Product, self).save(*args, **kwargs)
        self.pk_for_telegram = f'p||{self.pk}' # Короткий слаг из id для индентификации товара в боте
        super(Product, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('online_shop:product_detail', kwargs={'subcategory_slug': self.subcategory.slug, 'product_slug': self.slug})

    def __str__(self):
        return self.title


class ReceptionProduct(models.Model):
    '''Модель пополнения кол-ва товара (приемка)'''
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text='Товар')
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


class TelegramUser(models.Model):
    '''Модель юзеров из телеграма'''
    chat_id = models.IntegerField(unique=True, help_text='Id пользователя телеграм')
    first_name = models.CharField(max_length=255, blank=True, null=True, help_text='Имя')
    last_name = models.CharField(max_length=255, blank=True, null=True, help_text='Фамилия')
    username = models.CharField(max_length=255, blank=True, null=True, help_text='Юзернейм')
    fio = models.CharField(max_length=255, blank=True, null=True, help_text='ФИО для доставки')
    address = models.TextField(blank=True, null=True, help_text='Адрес доставки')
    number = models.BigIntegerField(blank=True, null=True, help_text='Телефон пользователя')
    post_index = models.IntegerField(blank=True, null=True, help_text='Почтовый индекс')
    search_data = models.CharField(max_length=255, blank=True, null=True, help_text='Данные для поиска товара')

    def __str__(self):
        return f"{self.chat_id} -- {self.username}"


class TelegramProductCartCounter(models.Model):
    '''Модель для каунтера и корзины, используется для клавиатуры добавления в корзину'''
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, help_text='Юзер')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text='Товар')
    count = models.IntegerField(default=1, help_text='Кол-во товара')
    counter = models.BooleanField(default=True, help_text='Если True, берет значение count для отображения в клавиатуре')

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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text='Продукт')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Цена на момент продажи')    
    count = models.IntegerField(help_text='Кол-во проданного товара')
    date = models.DateTimeField(auto_now_add=True, help_text='Дата и время продажи')
    payment_bool = models.BooleanField(default=False, help_text='Произведена ли оплата')
    

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
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, help_text='Юзер')
    delivery_pay = models.IntegerField(help_text='Стоимость доставки')
    sold_product = models.ManyToManyField(SoldProduct, help_text='Товары в заказе')  # <==== тут
    track_code = models.BigIntegerField(blank=True, null=True, help_text='Трек-код заказа')
    check_admin = models.BooleanField(default=False) # Использовалось для qiwi, что то с этим сделать
    datetime = models.DateTimeField(auto_now_add=True, help_text='Дата и время создания заказа')
    fio = models.CharField(max_length=255, blank=True, null=True, help_text='ФИО для доставки')     # Дублируется на случай если юзер удалит или поменяет данные для доставки
    address = models.TextField(blank=True, null=True, help_text='Адрес доставки')
    number = models.BigIntegerField(blank=True, null=True, help_text='Номер телефона пользователя')
    post_index = models.BigIntegerField(blank=True, null=True, help_text='Почтовый индекс')
    payment_bool = models.BooleanField(default=False, help_text='Оплачен ли заказ') # что то с этим сделать
    qiwi_bool = models.BooleanField(default=False, help_text='Способ оплаты - киви')


    def get_order_price(self):
        return sum([x.count * x.price for x in self.sold_product.all()]) + self.delivery_pay

    def get_datetime(self):
        user_timezone = pytz.timezone(settings.TIME_ZONE)
        datetime = self.datetime.astimezone(user_timezone)
        return datetime.strftime('%m/%d/%Y %H:%M')

###########################################################################
