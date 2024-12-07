from celery import shared_task
from django.utils import timezone
from .models import TenantApplication

@shared_task
def suspend_expired_tenants():
    expired_tenants = TenantApplication.objects.filter(
        expiration_date__lt=timezone.now().date(), 
        status='active'
    )

    for tenant in expired_tenants:
        tenant.status = 'suspended'
        tenant.save()

    return f"{len(expired_tenants)} tenants suspended"
