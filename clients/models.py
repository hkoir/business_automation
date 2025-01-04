from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.contrib.auth.models import AbstractUser


app_name='clients'

class Client(TenantMixin):
    name = models.CharField(max_length=100) 
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name


class Domain(DomainMixin):
    pass




class TenantData(models.Model):
    tenant = models.ForeignKey(Client,on_delete=models.CASCADE,related_name='tenant',null=True,blank=True)
    name = models.CharField(max_length=100) 
    subdomain = models.CharField(max_length=100, unique=True)  
    email = models.EmailField()  
    phone_number = models.CharField(max_length=20, blank=True, null=True)  
    address = models.TextField(blank=True, null=True)  
    created_on = models.DateTimeField(auto_now_add=True)  
    expiration_date = models.DateField(null=True, blank=True)    
    status_choices = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
    ]
    status = models.CharField(
        max_length=10,
        choices=status_choices,
        default='active'
    )
    approved_on = models.DateTimeField(null=True, blank=True) 
    rejection_reason = models.TextField(blank=True, null=True)  

    def __str__(self):
        return f"Application from {self.name} ({self.subdomain})"

    class Meta:
        ordering = ['-created_on'] 








class TenantInfo(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField() 

    def __str__(self):
        return self.name
