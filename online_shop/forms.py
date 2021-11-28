from django import forms
from .models import Review
from django.forms import NumberInput
# from main_app.models import OrderingProduct, OrderSiteProduct
from .models import OrderSiteProduct

class ReviewForm(forms.ModelForm):
    '''Форма отзыва о товаре'''
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {'text': forms.Textarea(attrs={'class': 'form-control shadow px-2', 'rows': 6}),
                   'rating': forms.RadioSelect}

class CartAddProductForm(forms.Form):
    '''Форма кол-ва товара в коризне и на странице продукта'''
    quantity = forms.IntegerField(min_value=1, widget=NumberInput(attrs={'class': 'form-control text-center px-3', 'value': 1}))

from main_app.management.commands.utils import check_price_delivery
class OrderCreateForm(forms.ModelForm):
    '''Форма создания заказа'''

    def clean_postal_code(self):
        data = self.cleaned_data['postal_code']
        try:
            check_postal = check_price_delivery(data, 1)
            return data
        except:
            raise forms.ValidationError("Не правильный индекс!")

    class Meta:
        model = OrderSiteProduct
        fields = ['first_name', 'last_name', 'email', 'telephone',
                  'address', 'postal_code', 'city', 'note']

        widgets = {
        'first_name': forms.TextInput(attrs={'class': 'form-control'}),
        'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        'email': forms.TextInput(attrs={'class': 'form-control'}),
        'telephone': forms.TextInput(attrs={'class': 'form-control'}),
        'address': forms.TextInput(attrs={'class': 'form-control'}),
        'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
        'city': forms.TextInput(attrs={'class': 'form-control'}),
        'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 1})
                            }