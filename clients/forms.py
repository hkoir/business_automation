from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import TenantData



class TenantApplicationForm(forms.ModelForm):
    class Meta:
        model = TenantData
        fields = ['name', 'subdomain', 'email', 'phone_number', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }
