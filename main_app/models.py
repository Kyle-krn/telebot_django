from django.db import models
from django.contrib.auth.models import User
# from django.utils.text import slugify
from slugify import slugify


class Category(models.Model):
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='category_img/')
    slug = models.CharField(max_length=255, unique=True, blank=True, null=True)
    max_count_product = models.IntegerField()

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, db_index=True)
    photo = models.ImageField(upload_to='subcategory_img/')
    slug = models.CharField(max_length=255, unique=True, blank=True, null=True)

    def __str__(self):
        return self.name



class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название товара')
    photo = models.ImageField(upload_to='product_img/')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.IntegerField(default=0)
    slug = models.CharField(max_length=255, unique=True, blank=True, null=True)
    # Закупочная стоймость
    subcategory = models.ForeignKey(
    SubCategory, on_delete=models.CASCADE)
    weight = models.IntegerField()


    def __str__(self):
        return self.title


class ReceptionProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    note = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    liquidated = models.BooleanField(default=False)

    def get_my_model_name(self):
        return self._meta.model_name

    def __str__(self):
        return f"{self.product} -- {self.count}"


class SoldProduct(models.Model):
    user = models.IntegerField(blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def get_my_model_name(self):
        return self._meta.model_name

    def __str__(self):
        return f"{self.product} -- {self.count}"


class TelegramUser(models.Model):
    chat_id = models.IntegerField(unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    fio = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    number = models.IntegerField(blank=True, null=True)
    post_index = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.chat_id} -- {self.username}"


class TelegramProductCartCounter(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # price = models.DecimalField(max_digits=10, decimal_places=2)    # Удалить прайс, он есть в продукте
    count = models.IntegerField(default=1)
    counter = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} -- {self.count}"


class PayProduct(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    product_pay = models.IntegerField()
    pay_comment = models.CharField(max_length=255)
    delivery_pay = models.IntegerField()
    datetime = models.DateTimeField(auto_now_add=True)





