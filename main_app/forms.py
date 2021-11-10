from django import forms
from django.forms import fields
from .models import *
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User



class ProductForm(forms.ModelForm):
      title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
      description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
      price = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number'}))
      weight = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number'}))
      photo = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))
      
      class Meta:
            model = Product
            fields = '__all__'
            fields = ['title', 'photo', 'description', 'price', 'subcategory', 'weight']


class Product_reqForm(ProductForm):
      photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))



class CategoryForm(forms.ModelForm):
      name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя новой категории'}))
      photo = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))
      max_count_product = forms.IntegerField( widget=forms.TextInput(attrs={'placeholder': 'Кол-во макс. товара', 'type': 'number'}))
      

      class Meta:
            model = Category
            fields = ['name', 'photo', 'max_count_product']

class Category_reqForm(CategoryForm):
      photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))


class SubcategoryForm(forms.ModelForm):
      name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя новой подкатегории'}))
      photo = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))

      class Meta:
            model = SubCategory
            fields = ['category' ,'name', 'photo']
            

class Subcategory_reqForm(SubcategoryForm):
      photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

      class Meta:
            model = SubCategory
            fields = ['name', 'photo']


class ReceptionForm(forms.ModelForm):
      price = forms.IntegerField(label='Закупочная цена', widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number'}))
      count = forms.IntegerField(label='Кол-во товара', widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number'}))
      note = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поле для заметки'}))

      class Meta:
            model = ReceptionProduct
            fields = ['price', 'count', 'note', 'product']


class ReceptionForProductViewForm(ReceptionForm):
      class Meta:
            model = ReceptionProduct
            fields = ['price', 'count', 'note']


class QiwiTokenForm(forms.ModelForm):
      number = forms.IntegerField(label='Номер телефона', widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'pattern': '[0-9]{11}'}))
      token = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поле для токена', 'type': 'text', 'minlength': 32, 'maxlength': 32}))

      class Meta:
            model = QiwiToken
            fields = ['number', 'token']

class TrackCodeForm(forms.ModelForm):
      # track_code = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form_control', 'type': 'text'}))
      class Meta:
            model = OrderingProduct
            fields = ['track_code']


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}))


class ProductDeleteForm(forms.ModelForm):
      id = forms.CharField(widget=forms.HiddenInput())

      class Meta:
            model = Product
            fields = ['id']

      def clean_id(self):
            data = self.cleaned_data['id']
            try:
                  Product.objects.get(pk=data)
                  return data
            except:
                  raise forms.ValidationError("Не верный id товара!")


class OrderChangeForm(forms.ModelForm):
      # id = forms.CharField(widget=forms.HiddenInput())
      count = forms.IntegerField(label='Кол-во товара:', widget=forms.TextInput(attrs={'min': 1 , 'type': 'number', 'style': 'width: 25%'}))

      class Meta:
            model = SoldProduct
            fields = ['count']

class HiddenOrderIdForm(forms.Form):
      id = forms.CharField(widget=forms.HiddenInput())
      

      def clean_id(self):
            data = self.cleaned_data['id']
            try:
                  OrderingProduct.objects.get(pk=data)
                  return data
            except:
                  raise forms.ValidationError("Не верный id заказа!")


class TrackCodeOrderForm(HiddenOrderIdForm):
      track_code = forms.CharField()

