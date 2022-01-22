from django.contrib.auth.forms import AuthenticationForm
from django import forms
from online_shop.models import OrderSiteProduct
from .models import *

class ProductForm(forms.ModelForm):
      '''Форма для создания товара'''
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
      '''Форма для изменения товара'''
      photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))


class CategoryForm(forms.ModelForm):
      '''Форма создания категории'''
      name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя новой категории'}))
      photo = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))
      max_count_product = forms.IntegerField( widget=forms.TextInput(attrs={'placeholder': 'Кол-во макс. товара', 'type': 'number'}))
      

      class Meta:
            model = Category
            fields = ['name', 'photo', 'max_count_product']

class Category_reqForm(CategoryForm):
      '''Форма для изменения категории'''
      photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))



class SubcategoryForm(forms.ModelForm):
      '''Форма создания подкатегории'''
      name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя новой подкатегории'}))
      photo = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))

      class Meta:
            model = SubCategory
            fields = ['category' ,'name', 'photo']
            

class Subcategory_reqForm(SubcategoryForm):
      '''Форма изменения подкатегории'''
      photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

      class Meta:
            model = SubCategory
            fields = ['name', 'photo']


class ReceptionForm(forms.ModelForm):
      '''Форма для приемки товара на отдельной странице'''
      price = forms.IntegerField(label='Закупочная цена', widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number'}))
      count = forms.IntegerField(label='Кол-во товара', widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number'}))
      note = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поле для заметки'}))

      class Meta:
            model = ReceptionProduct
            fields = ['price', 'count', 'note', 'product']


class ReceptionForProductViewForm(ReceptionForm):
      '''Форма приемки товара на станице товара'''
      class Meta:
            model = ReceptionProduct
            fields = ['price', 'count', 'note']


class QiwiTokenForm(forms.ModelForm):
      '''Форма добавления киви токена'''
      number = forms.IntegerField(label='Номер телефона', widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'pattern': '[0-9]{11}'}))
      token = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поле для токена', 'type': 'text', 'minlength': 32, 'maxlength': 32}))

      class Meta:
            model = QiwiToken
            fields = ['number', 'token']

class TrackCodeForm(forms.ModelForm):
      '''Форма добавления трек кода'''
      # track_code = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form_control', 'type': 'text'}))
      class Meta:
            model = OrderingProduct
            fields = ['track_code']


class LoginUserForm(AuthenticationForm):
      '''Форма аутентификации'''
      username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input'}))
      password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}))


class ProductDeleteForm(forms.ModelForm):
      '''Форма удаления товара'''
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


class OrderChangeForm(forms.Form):
      '''Форма изменения кол-ва товара в заказе'''
      count = forms.IntegerField(label='Кол-во товара:', widget=forms.TextInput(attrs={'min': 1 , 'type': 'number', 'style': 'width: 25%'}))

      def clean_count(self):
            data = self.cleaned_data['count']
            if data < 1:
                  data = 1
            return data

      

class HiddenOrderIdForm(forms.Form):
      '''Скрытый id для индентификации заказа, используется на вкладках с заказами'''
      id = forms.IntegerField(widget=forms.HiddenInput())
      

class TrackCodeForm(forms.Form):
      track_code = forms.CharField(required=False)


class QiwiIdForm(forms.Form):
      id = forms.IntegerField()

      def clean_id(self):
            data = self.cleaned_data['id']
            try:
                  QiwiToken.objects.get(pk=data)
                  return data
            except:
                  raise forms.ValidationError("Не верный id токена")


class PaidOrderSiteForm(forms.ModelForm):
      '''Форма изменения статуса заказа и трек номера заказа через сайт'''
      id = forms.IntegerField()
      track_code = forms.CharField(required=False)
      # status = forms.ChoiceField()

      class Meta:
            model = OrderSiteProduct
            fields = ['id', 'status', 'track_code']
