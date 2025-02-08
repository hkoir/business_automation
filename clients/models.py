from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.contrib.auth.models import AbstractUser,User
from datetime import timedelta
from django.utils import timezone


app_name='clients'



class Client(TenantMixin):
    name = models.CharField(max_length=100) 
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name


class Domain(DomainMixin):
    pass


  

class SubscriptionPlan(models.Model):
    DURATION_CHOICES = [
        (6, '6 Months'),
        (12, '1 Year'),
        (24, '2 Years'),
        (36, '3 Years'),
        (48, '4 Years'),
        (60, '5 Years'),
    ]

    duration = models.PositiveIntegerField(choices=DURATION_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    description = models.TextField(blank=True, null=True)  
    features = models.TextField()  # Comma-separated features
    created_on = models.DateTimeField(auto_now_add=True)  
    updated_on = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f"{self.get_duration_display()} - ${self.price}"


class Tenant(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True, related_name='tenant_user')
    tenant = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='tenant', null=True, blank=True)  # Maps to Client
    name = models.CharField(max_length=100)
    subdomain = models.CharField(max_length=100, unique=True)  
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='tenant_lgo',blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)  
    updated_on = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f"{self.name} ({self.subdomain})"




class Subscription(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='subscription')
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateField(auto_now_add=True)
    expiration_date = models.DateField(null=True, blank=True)
    is_renewal = models.BooleanField(default=False) 
    is_expired = models.BooleanField(default=False) 
    status_choices = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='active')
    approved_on = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)  
    updated_on = models.DateTimeField(auto_now=True)  

    def is_expired(self):
        return self.expiration_date and self.expiration_date < timezone.now().date()

    def renew_subscription(self, new_plan):
        self.subscription_plan = new_plan
        self.start_date = timezone.now().date()
        self.expiration_date = timezone.now().date() + timedelta(days=new_plan.duration * 30)  # Assuming 30 days per month
        self.status = 'active'
        self.save()

    def __str__(self):
        return f"{self.tenant.name} - {self.subscription_plan}"

    class Meta:
        ordering = ['-start_date']


class TenantInfo(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField() 
    def __str__(self):
        return self.name



class PaymentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="payment_profile")
    payment_token = models.CharField(max_length=255, unique=True)  # Token from payment gateway
    card_last4 = models.CharField(max_length=4, blank=True, null=True)  # Last 4 digits
    card_brand = models.CharField(max_length=50,
    choices=[
        ('VISA','Visa'),
        ('MASTER-CARD','Master card'),
         ('AMEX','American Express')
        ], blank=True, null=True)  
    card_expiry_month = models.IntegerField(blank=True, null=True)  # Expiry month
    card_expiry_year = models.IntegerField(blank=True, null=True)  # Expiry year
