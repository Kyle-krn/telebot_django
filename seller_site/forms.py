from .models import *
from django import forms

class OfflineProductForm(forms.ModelForm):
      title = forms.CharField(label='Название', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название товара'}))
      price = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'placeholder': 'Введите цену для продажи'}))
      purchase_price = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'placeholder': 'Введите закупочную цену'}))
      
      class Meta:
            model = OfflineProduct
            fields = '__all__'
            fields = ['title', 'price', 'subcategory', 'purchase_price']

class OffilneCategoryForm(forms.ModelForm):
      name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя новой категории'}))

      class Meta:
            model = OfflineCategory
            fields = ['name']


class OfflineSubcategoryForm(forms.ModelForm):
      name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя новой подкатегории'}))

      class Meta:
            model = OfflineSubCategory
            fields = ['name']