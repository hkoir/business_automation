
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

from.models import UserProfile
from django.core.exceptions import ValidationError
from .models import UserProfile, Client




class CustomLoginForm(AuthenticationForm):
    tenant = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Tenant', 
            'readonly': 'readonly'
        }),
        label="Tenant",
    )
    class Meta:
        model = AuthenticationForm
        fields = ['username', 'password','tenant']

       


class TenantUserRegistrationForm(UserCreationForm):
    tenant = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Tenant', 
            'readonly': 'readonly'
        }),
        label="Tenant",
    )
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'tenant','password1', 'password2','profile_picture']

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)

        if tenant:
            self.fields['tenant'].initial = tenant
            self.fields['tenant'].disabled = True

    def clean_tenant(self):
        tenant = self.cleaned_data['tenant']
        if not tenant:
            raise ValidationError("Tenant is required.")
        return tenant

    def save(self, commit=True):
        user = super().save(commit=False)
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise ValidationError("The passwords do not match.")
        user.set_password(password1)

        if commit:
            user.save()

        tenant = self.cleaned_data['tenant']
        tenant_instance = Client.objects.get(schema_name=tenant)  

        user_profile = UserProfile(
            user=user,
            tenant=tenant_instance,
            profile_picture=self.cleaned_data.get('profile_picture')  
        )

        if commit:
            user_profile.save()

        return user




class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class CustomUserCreationForm(UserCreationForm):
    address = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=100, required=False)
    postal_code = forms.CharField(max_length=20, required=False)
    country = forms.CharField(max_length=100, required=False)
    phone_number = forms.CharField(max_length=20, required=False)
    profile_picture = forms.ImageField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'address', 'city', 'state', 'postal_code', 'country', 'phone_number','profile_picture']


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']











from django.contrib.auth.forms import (AuthenticationForm, PasswordResetForm,SetPasswordForm)

class PwdResetForm(PasswordResetForm):
    email = forms.EmailField(max_length=254, widget=forms.TextInput(
        attrs={'class': 'form-control mb-3', 'placeholder': 'Email', 'id': 'form-email'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        u = User.objects.filter(email=email)
        if not u:
            raise forms.ValidationError(
                'Unfortunatley we can not find that email address')
        return email




class PwdResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='New password', widget=forms.PasswordInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'New Password', 'id': 'form-newpass'}))
    new_password2 = forms.CharField(
        label='Repeat password', widget=forms.PasswordInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'New Password', 'id': 'form-new-pass2'}))




