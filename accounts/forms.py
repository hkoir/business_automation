
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

from.models import UserProfile


class CustomLoginForm(AuthenticationForm):
    class Meta:
        model = AuthenticationForm
        fields = ['username', 'password']


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