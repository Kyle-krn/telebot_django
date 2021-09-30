from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255)
    # slug = models.SlugField(max_length=70, unique=True)

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, db_index=True)
    # slug = models.SlugField(max_length=150, unique=True, db_index=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название товара')
    photo = models.ImageField(upload_to='product_img/')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.IntegerField()
    # Закупочная стоймость

    subcategory = models.ForeignKey(
    SubCategory, on_delete=models.CASCADE)

    # slug = models.SlugField(max_length=70, unique=True)

    def __str__(self):
        return self.title
