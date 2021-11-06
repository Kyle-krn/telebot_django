from django import forms
from .models import Review
from django.forms import NumberInput

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {'text': forms.Textarea(attrs={'class': 'form-control shadow px-2', 'rows': 6}),
                   'rating': forms.RadioSelect}

class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, widget=NumberInput(attrs={'class': 'form-control text-center px-3', 'value': 1}))