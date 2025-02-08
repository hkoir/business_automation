
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.conf import settings

import pkg_resources
from django.contrib.auth.models import User, Permission
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import (AuthenticationForm, PasswordResetForm,SetPasswordForm)
from.models import UserProfile,Client





class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'tenant']

    def __init__(self, *args, **kwargs):
        user = kwargs.get('instance').user if 'instance' in kwargs else None
        if user:    
            tenant = user.user_profile.tenant if user.user_profile else None
            kwargs['initial'] = kwargs.get('initial', {})
            kwargs['initial']['tenant'] = tenant
        super(UserProfileForm, self).__init__(*args, **kwargs)


    

class CustomLoginForm(AuthenticationForm):
    tenant = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Tenant', 
            'readonly':'readonly'
          
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




MODEL_CHOICES = [
    ('purchase.PurchaseRequestOrder', 'Purchase Request Order'),
    ('purchase.PurchaseOrder', 'Purchase Order'),
    ('sales.SaleRequestOrder', 'Sales Request Order'),    
    ('sales.SaleOrder', 'Sales Order'),   
    ('manufacture.MaterialsRequestOrder', 'Production Materials Request Order'),  
]


class AssignPermissionsForm(forms.Form):       
    model_name = forms.ChoiceField(
        choices=MODEL_CHOICES,  
        label="Select Model"
    )
    # user = forms.ModelChoiceField(queryset=User.objects.all(), label="Select User",required=False)
    email = forms.EmailField(label="Enter User's Email Address")
    permissions = forms.MultipleChoiceField(
        choices=
        [
        ('can_request', 'Can Request'),
        ('can_review', 'Can Review'),
        ('can_approve', 'Can Approve')
        ],
        widget=forms.CheckboxSelectMultiple,
        label="Assign Permissions"
    )

    def clean(self):
        cleaned_data = super().clean()
        model_name = cleaned_data.get('model_name')
        permission_codename = cleaned_data.get('permission_codename')

        if model_name and permission_codename:
            app_label, model_label = model_name.split('.')
            model = apps.get_model(app_label, model_label)            

            try:
                content_type = ContentType.objects.get_for_model(model)
                permission = Permission.objects.get(codename=permission_codename, content_type=content_type)
            except Permission.DoesNotExist:
                raise forms.ValidationError(f"Permission '{permission_codename}' does not exist for the selected model.")
            
        return cleaned_data



class UserGroupForm(forms.Form):
    username = forms.CharField(max_length=100, label="Username")
    email = forms.EmailField(label="Enter User's Email Address")
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label="Select Group", required=False)
    new_group_name = forms.CharField(max_length=100, label="New Group Name", required=False)

    def clean(self):
        cleaned_data = super().clean()
        group = cleaned_data.get("group")
        new_group_name = cleaned_data.get("new_group_name")

        if not group and not new_group_name:
            raise forms.ValidationError("You must either select an existing group or provide a new group name.")
        
        return cleaned_data



class AssignPermissionsToGroupForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label="Select Group")
    model_name = forms.ChoiceField(choices=MODEL_CHOICES, label="Select Model", widget=forms.Select(attrs={'id': 'model-select'}))

    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),  # Initially empty until model is selected
        widget=forms.CheckboxSelectMultiple(attrs={'id': 'permissions-select'}),
        label="Select Permissions",
        required=False
    )

    def __init__(self, *args, **kwargs):
        model_name = kwargs.get('initial', {}).get('model_name', None)
        super().__init__(*args, **kwargs)
        if model_name:
            model_class = apps.get_model(*model_name.split('.'))
            content_type = ContentType.objects.get_for_model(model_class)
            self.fields['permissions'].queryset = Permission.objects.filter(content_type=content_type)


