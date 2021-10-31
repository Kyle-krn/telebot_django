from django.contrib import admin
from .models import *
# Register your models here.
from django import forms
from django.db import models



class OfflineOrderingProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'datetime', 'price') 


class OfflineSoldProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'product', 'price', 'count', 'date','price_for_seller', 'order') 

class OfflineReceptionProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'note', 'price', 'count', 'date','liquidated')





admin.site.register(OfflineOrderingProduct, OfflineOrderingProductAdmin)
admin.site.register(OfflineSoldProduct, OfflineSoldProductAdmin)
admin.site.register(OfflineReceptionProduct, OfflineReceptionProductAdmin)