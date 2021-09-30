from django import forms
from .models import *

MEDIA_CHOICES = (
 ('Audio', (
   (1, 'Vinyl'),
   (2, 'CD'),
  )
 ),
 ('Video', (
   ('3', 'VHS Tape'),
   ('4', 'DVD'),
  )
 ),
)

GEEKS_CHOICES =(
    ("1", "One"),
    ("2", "Two"),
    ("3", "Three"),
    ("4", "Four"),
    ("5", "Five"),
)

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

