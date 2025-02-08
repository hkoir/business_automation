from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Tenant,Subscription



class TenantApplicationForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['name', 'subdomain','email','phone_number', 'address','logo']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }




from django import forms

class CreditCardPaymentForm(forms.Form):
    CARD_BRAND_CHOICES = [
        ('Visa', 'Visa'),
        ('MasterCard', 'MasterCard'),
        ('Amex', 'American Express'),
        ('Discover', 'Discover'),
    ]

    card_number = forms.CharField(
        max_length=16,
        label="Card Number",
        widget=forms.TextInput(attrs={'placeholder': 'Enter your card number', 'class': 'form-control'})
    )
    expiry_date = forms.CharField(
        max_length=5,
        label="Expiry Date (MM/YY)",
        widget=forms.TextInput(attrs={'placeholder': 'MM/YY', 'class': 'form-control'})
    )
    cvv = forms.CharField(
        max_length=3,
        label="CVV",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter CVV', 'class': 'form-control'})
    )
    card_brand = forms.ChoiceField(
        choices=CARD_BRAND_CHOICES,
        label="Card Brand",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean_card_number(self):
        card_number = self.cleaned_data['card_number']
        if not card_number.isdigit() or len(card_number) != 16:
            raise forms.ValidationError("Invalid card number.")
        return card_number

    def clean_expiry_date(self):
        expiry_date = self.cleaned_data['expiry_date']
        if not expiry_date or len(expiry_date) != 5 or '/' not in expiry_date:
            raise forms.ValidationError("Invalid expiry date format. Use MM/YY.")
        month, year = expiry_date.split('/')
        if not month.isdigit() or not year.isdigit() or not (1 <= int(month) <= 12):
            raise forms.ValidationError("Invalid expiry date.")
        return expiry_date

    def clean_cvv(self):
        cvv = self.cleaned_data['cvv']
        if not cvv.isdigit() or len(cvv) != 3:
            raise forms.ValidationError("Invalid CVV.")
        return cvv

