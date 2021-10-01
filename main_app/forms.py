from django import forms
from .models import *


class ProductForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    price = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    count = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))


    class Meta:
        model = Product
        fields = '__all__'
        # fields = ['title', 'photo', 'description', 'price', 'count', 'subcategory']

class CategoryForm(forms.ModelForm):
      name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя новой категории'}))
      photo = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))

      class Meta:
            model = Category
            fields = ['name', 'photo']

class SubcategoryForm(forms.ModelForm):
      name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя новой подкатегории'}))
      photo = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))

      class Meta:
            model = SubCategory
            fields = ['name', 'photo']