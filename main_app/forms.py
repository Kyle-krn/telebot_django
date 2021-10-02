from django import forms
from .models import *


class Product_reqForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    price = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number'}))
    count = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'readonly': True}))
    photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Product
      #   fields = '__all__'
        fields = ['title', 'photo', 'description', 'price', 'count', 'subcategory']

class ProductForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    price = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number'}))
    count = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'readonly': True}))
    photo = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Product
        fields = '__all__'
        fields = ['title', 'photo', 'description', 'price', 'count', 'subcategory']

class CategoryForm(forms.ModelForm):
      name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя новой категории'}))
      photo = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))

      class Meta:
            model = Category
            fields = ['name', 'photo']

class Category_reqForm(forms.ModelForm):
      name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя новой категории'}))
      photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

      class Meta:
            model = Category
            fields = ['name', 'photo']

class SubcategoryForm(forms.ModelForm):
      name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя новой подкатегории'}))
      photo = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))

      class Meta:
            model = SubCategory
            fields = ['name', 'photo']


class Subcategory_reqForm(forms.ModelForm):
      name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя новой подкатегории'}))
      photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

      class Meta:
            model = SubCategory
            fields = ['name', 'photo']


class ReceptionForm(forms.ModelForm):
      price = forms.IntegerField(label='Закупочная цена', widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number'}))
      count = forms.IntegerField(label='Кол-во товара', widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number'}))

      class Meta:
            model = ReceptionSoldProduct
            fields = ['price', 'count']