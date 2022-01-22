from django.db import models
from django.db.models.query_utils import Q
from django.urls import reverse
from django.utils.timezone import pytz
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from pytils.translit import slugify


class Category(models.Model):
    '''Модель категорий'''
    name = models.CharField(max_length=255, help_text='Имя категории')
    photo = models.ImageField(upload_to='category_img/', help_text='Фото категории')
    slug = models.SlugField(max_length=100, unique=True)
    pk_for_telegram = property(fget=lambda self: f'c||{self.pk}')    # Нужен для идентификации в телеграм боте
    max_count_product = models.IntegerField()

    def save(self, *args, **kwargs):
        if self.pk is not None:
            old_self = Category.objects.get(pk=self.pk)
            if old_self.photo and self.photo != old_self.photo:
                old_self.photo.delete(False)

        self.slug = slugify(self.name)
        return super(Category, self).save(*args, **kwargs)

    def get_absolute_url_for_shop(self):
        return reverse('online_shop:product_list_by_category', kwargs={'category_slug': self.slug})
        
    def __str__(self):
        return self.name

@receiver(pre_delete, sender=Category)
def photo_delete(sender, instance, **kwargs):
    if instance.photo.name:
        instance.photo.delete(False)


class SubCategory(models.Model):
    '''Модель подкатегорий'''
    category = models.ForeignKey(Category, on_delete=models.CASCADE, help_text='Категория подкатегории')
    name = models.CharField(max_length=150, db_index=True, help_text='Имя подкатегории')
    photo = models.ImageField(upload_to='subcategory_img/', help_text='Фотоподкатегории')
    slug = models.SlugField(max_length=100, unique=True)
    pk_for_telegram = property(fget=lambda self: f'sc||{self.pk}')

    def save(self, *args, **kwargs):
        if self.pk is not None:
            old_self = SubCategory.objects.get(pk=self.pk)
            if old_self.photo and self.photo != old_self.photo:
                old_self.photo.delete(False)

        self.slug = slugify(self.name)
        return super(SubCategory, self).save(*args, **kwargs)


    def get_absolute_url_for_shop(self):
        return reverse('online_shop:product_list_by_subcategory', kwargs={'category_slug': self.category.slug, 'subcategory_slug': self.slug})

    def __str__(self):
        return self.name


@receiver(pre_delete, sender=SubCategory)
def photo_delete(sender, instance, **kwargs):
    if instance.photo.name:
        instance.photo.delete(False)


class Product(models.Model):
    '''Модель товара'''
    title = models.CharField(max_length=255, verbose_name='Название товара')
    photo = models.ImageField(upload_to='product_img/', help_text='Фото товара')
    description = models.TextField(help_text='Описание товара')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Цена товара')
    count = models.IntegerField(default=0, help_text='Остаток на складе')
    slug = models.SlugField(max_length=100, unique=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, help_text='Подкатегория товара')
    weight = models.IntegerField(help_text='Вес товара')    # Вес нужен для автоматического расчета стоймости доставки заказа
    pk_for_telegram = property(fget=lambda self: f'p||{self.pk}')

    def get_average_review_score(self):
        '''В данный момент не используется, используется в онлайн магазине для расчитывания рейтинга товара из отызвов'''
        average_score = 0.0
        if self.reviews.count() > 0:
            total_score = sum([review.rating for review in self.reviews.all()])
            average_score = total_score / self.reviews.count()
            return round(average_score, 1)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            old_self = Product.objects.get(pk=self.pk)
            if old_self.photo and self.photo != old_self.photo:
                old_self.photo.delete(False)

        self.slug = slugify(self.title)
        return super(Product, self).save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse('admin_panel:productdetail', kwargs={'pk': self.pk})


    def get_absolute_url_for_shop(self):
        return reverse('online_shop:product_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title


@receiver(pre_delete, sender=Product)
def photo_delete(sender, instance, **kwargs):
    if instance.photo.name:
        instance.photo.delete(False)


class ReceptionProduct(models.Model):
    '''Модель пополнения кол-ва товара (приемка)'''
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text='Товар')
    note = models.CharField(max_length=255, blank=True, null=True, help_text='Заметка приемки')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Закупочная цена')
    count = models.IntegerField(help_text='Кол-во товара в приемке')
    date = models.DateTimeField(auto_now_add=True, help_text='Дата и время приемки')
    liquidated = models.BooleanField(default=False, help_text='Ликвидация товара') # True для ликвидированного товара

    def save(self, *args, **kwargs):
        '''Обновляет кол-во товара в OfflineProduct'''
        if self.count <= 0:
            return
        if self.liquidated:
            self.product.count -= self.count
        else:
            self.product.count += self.count
        self.product.save()
        return super(ReceptionProduct, self).save(*args, **kwargs)

    def get_datetime(self):
        '''Возвращает московское время'''
        user_timezone = pytz.timezone(settings.TIME_ZONE)
        datetime = self.date.astimezone(user_timezone)
        return datetime.strftime('%m/%d/%Y %H:%M')

    def get_my_model_name(self):
        '''Возвращает имя модели, используется в детальном представлении товара, для подсвечивания строк в таблице (приемка, продажа, ликвидация)'''
        return self._meta.model_name

    def __str__(self):
        if self.liquidated:
            return f"Ликвидировано {self.count} шт. | {self.product}"
        return f"Добавленно {self.count} шт. | {self.product}"


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
        if not self.username:
            return f"#{self.chat_id}|Пользователь скрыл свой юзернейм"
        return f"{self.username}"


class TelegramProductCartCounter(models.Model):
    '''Модель с counter=True используется в боте для передачи значения кол-ва в клавитуру на странице товара,
    когда пользователь нажимает - добавить в корзину, counter становится False.
    Counter=True для юзера должен быть только 1 или 0 в БД. Остальные записи где counter=False относиться к корзине юзера в телеграме
    '''
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, help_text='Юзер')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text='Товар')
    count = models.IntegerField(default=1, help_text='Кол-во товара')
    counter = models.BooleanField(default=True, help_text='Если True, берет значение count для отображения в клавиатуре')

    

    def __str__(self):
        return f"{self.user} -- {self.count} шт."


class PayProduct(models.Model):
    '''Модель бронирования товара на оплату -  используется для оплаты через qiwi'''
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    product_pay = models.IntegerField()
    pay_comment = models.CharField(max_length=255)
    delivery_pay = models.IntegerField()
    datetime = models.DateTimeField(auto_now_add=True)


    def cancel_reservation(self):
        cart = TelegramProductCartCounter.objects.filter(Q(user=self.user) & Q(counter=False))
        for item in cart:
            item.product.count += item.count
            item.product.save()
        return self.delete()

    def save(self, *args, **kwargs):
        cart = TelegramProductCartCounter.objects.filter(Q(user=self.user) & Q(counter=False))
        for item in cart: 
            item.product.count -= item.count
            item.product.save()
        return super(PayProduct, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Оплата {self.product_pay+ self.delivery_pay} руб.|Коментарий для оплаты {self.pay_comment}"


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
    order = models.ForeignKey('OrderingProduct', related_name='soldproduct', on_delete=models.CASCADE, help_text='Заказ')

    def return_in_product(self, new_count):
        '''Изменяет кол-во товара при редактировании заказа'''
        self.product.count += (self.count - new_count)
        self.product.save()
        self.count = new_count
        return super(SoldProduct, self).save()
    
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
    # sold_product = models.ManyToManyField(SoldProduct, help_text='Товары в заказе')  # <==== тут
    track_code = models.CharField(blank=True, null=True, max_length=150, help_text='Трек-код заказа')
    check_admin = models.BooleanField(default=False) # Использовалось для qiwi, что то с этим сделать
    datetime = models.DateTimeField(auto_now_add=True, help_text='Дата и время создания заказа')
    fio = models.CharField(max_length=255, blank=True, null=True, help_text='ФИО для доставки')     # Дублируется на случай если юзер удалит или поменяет данные для доставки
    address = models.TextField(blank=True, null=True, help_text='Адрес доставки')
    number = models.BigIntegerField(blank=True, null=True, help_text='Номер телефона пользователя')
    post_index = models.BigIntegerField(blank=True, null=True, help_text='Почтовый индекс')
    payment_bool = models.BooleanField(default=False, help_text='Оплачен ли заказ') # что то с этим сделать
    qiwi_bool = models.BooleanField(default=False, help_text='Способ оплаты - киви')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text='Цена на момент продажи')  

    def set_order_price(self):
        '''Обновляет стоймость заказа при его изменении'''
        self.price = sum([x.price * x.count for x in self.soldproduct.all()])
        return self.save()

    def get_datetime(self):
        user_timezone = pytz.timezone(settings.TIME_ZONE)
        datetime = self.datetime.astimezone(user_timezone)
        return datetime.strftime('%m/%d/%Y %H:%M')

    def __str__(self):
        return f"Заказ #{self.pk}"



###########################################################################
