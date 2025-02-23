from django.contrib.auth.models import User
from django.db import models
from simple_history.models import HistoricalRecords
from clients.models import Client
from django.contrib.auth.models import AbstractUser

from django.contrib.auth import get_user_model





class CustomUser(AbstractUser):
    tenant = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.username} - {self.tenant.name if self.tenant else 'No Tenant'}"
    


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_profile')
    tenant = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='user_tenants', null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"