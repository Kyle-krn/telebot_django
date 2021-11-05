from django.db.models import fields
from .models import *
from django import forms
from django.contrib.auth.forms import  UserCreationForm


class RegisterUserForm(UserCreationForm):
      '''Форма регистрации продавца'''
      first_name = forms.CharField(label='Имя', widget=forms.TextInput(attrs={'class': 'form-control'}))
      last_name = forms.CharField(label='Фамилия', widget=forms.TextInput(attrs={'class': 'form-control'}))
      username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control'}))
      password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
      password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

      class Meta:
            model = User
            fields = ('username', 'password1', 'password2', 'first_name', 'last_name')

class OfflineProductForm(forms.ModelForm):
      '''Форма создания товара'''
      title = forms.CharField(label='Название', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название товара'}))
      price = forms.IntegerField(widget=forms.TextInput(attrs={'min': '1','class': 'form-control', 'type': 'number', 'placeholder': 'Введите цену для продажи'}))
      purchase_price = forms.IntegerField(widget=forms.TextInput(attrs={'min': 1,'class': 'form-control', 'type': 'number', 'placeholder': 'Введите закупочную цену'}))
      
      class Meta:
            model = OfflineProduct
            fields = '__all__'
            fields = ['title', 'price', 'subcategory', 'purchase_price']

class OffilneCategoryForm(forms.ModelForm):
      '''Форма создания категории'''
      name = forms.CharField(widget=forms.TextInput(attrs={'style': 'float: left; width: 60%;', 'class': 'form-control', 'placeholder': 'Введите имя новой категории'}))
      price_for_seller = forms.IntegerField(widget=forms.TextInput(attrs={'min': 0,'class': 'form-control', 'type': 'number', 'placeholder': 'Сумма для продовца'}))

      class Meta:
            model = OfflineCategory
            fields = ['name', 'price_for_seller']

class OffilneChangeCategoryForm(OffilneCategoryForm):
      '''Форма изменения категории'''
      id = forms.CharField(widget=forms.HiddenInput())
      price_for_seller = forms.IntegerField(widget=forms.TextInput(attrs={'min': 0,'class': 'form-control', 'type': 'number', 'placeholder': 'Сумма для продовца', 'style': 'float: left; width: 20%;'}))
      name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя новой категории', 'style': 'float: right; width: 75%;'}))

      class Meta:
            model = OfflineCategory
            fields = ['id', 'name', 'price_for_seller']

class OfflineSubcategoryForm(forms.ModelForm):
      '''Форма создаения подкатегории'''
      name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя новой подкатегории'}))

      class Meta:
            model = OfflineSubCategory
            fields = ['name', 'category']

class OfflineChangeSubcategoryForm(OfflineSubcategoryForm):
      id = forms.CharField(widget=forms.HiddenInput())

      class Meta:
            model = OfflineSubCategory
            fields = ['id', 'name']

class OfflineReceptionForm(forms.ModelForm):
      '''Форма создания приемки'''
      count = forms.IntegerField(label='Кол-во товара:', widget=forms.TextInput(attrs={'min': 1,'class': 'form-control', 'type': 'number'}))
      note = forms.CharField(required=False, label="Заметка:", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поле для заметки'}))

      class Meta:
            model = OfflineReceptionProduct
            fields = ['count', 'note', 'product']


class OfflineReceptionForProductViewForm(OfflineReceptionForm):
      class Meta:
            model = OfflineReceptionProduct
            fields = ['count', 'note']


class OrderChangeForm(forms.ModelForm):
      # id = forms.CharField(widget=forms.HiddenInput())
      count = forms.IntegerField(label='Кол-во товара:', widget=forms.TextInput(attrs={'min': 1 , 'type': 'number', 'style': 'width: 25%'}))

      class Meta:
            model = OfflineSoldProduct
            fields = ['count']
