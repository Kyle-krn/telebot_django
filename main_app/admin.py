from django.contrib import admin
from .models import *
# Register your models here.
from django import forms
from django.db import models



class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'price', 'count') 


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')

class ReceptionProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'count', 'price', 'date')

class SoldProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'count', 'price', 'date')



admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(ReceptionProduct, ReceptionProductAdmin)
admin.site.register(SoldProduct, SoldProductAdmin)
admin.site.register(TelegramProductCartCounter)
admin.site.register(TelegramUser)
admin.site.register(PayProduct)