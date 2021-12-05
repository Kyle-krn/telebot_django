from django import forms
from django.contrib.auth.models import User
from django.forms import widgets
from .models import Profile
from main_app.utils import check_price_delivery

class UserRegistrationForm(forms.ModelForm):
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password',)

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'})
        }

class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    widgets = {
        'first_name': forms.TextInput(attrs={'class': 'form-control'}),
        'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        'email': forms.EmailInput(attrs={'class': 'form-control'}),
    }

class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('phone_number', 'address', 'postal_code', 'city')
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'type': 'number'}),
            'city': forms.TextInput(attrs={'class': 'form-control'})
        }

    def clean_postal_code(self):
        data = self.cleaned_data['postal_code']
        try:
            check_postal = check_price_delivery(data, 1)
            return data
        except:
            raise forms.ValidationError("Не правильный индекс!")
        
