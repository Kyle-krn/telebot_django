from django.contrib import admin
from .models import *
# Register your models here.
from django import forms
from django.db import models


MEDIA_CHOICES = (
 ('Audio', (
   ('1', 'Vinyl'),
   ('2', 'CD'),
  )
 ),
 ('Video', (
   ('3', 'VHS Tape'),
   ('4', 'DVD'),
  )
 ),
)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'price', 'count') 


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)