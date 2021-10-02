from django.db import models
from django.contrib.auth.models import User
# from django.utils.text import slugify
from slugify import slugify


class Category(models.Model):
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='category_img/')
    slug = models.SlugField(max_length=70, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"cat||{self.name}"  
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, db_index=True)
    photo = models.ImageField(upload_to='subcategory_img/')
    slug = models.SlugField(max_length=150, unique=True, db_index=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"subcat||{self.category.name}||{self.name}")
        super(SubCategory, self).save(*args, **kwargs)


class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название товара')
    photo = models.ImageField(upload_to='product_img/')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.IntegerField()
    slug = models.SlugField(max_length=150, unique=True, db_index=True)
    # Закупочная стоймость
    subcategory = models.ForeignKey(
    SubCategory, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"product||{self.subcategory.name}||{self.title}")
        super(Product, self).save(*args, **kwargs)

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
