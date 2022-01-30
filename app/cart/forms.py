from django import forms


class CartAddProductForm(forms.Form):
    '''Форма кол-ва товара в коризне и на странице продукта'''
    quantity = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control text-center px-3', 'value': 1}))