from celery import shared_task
from django.utils import timezone
from clients.models import TenantApplication

@shared_task
def suspend_expired_tenants():
    current_date = timezone.now().date()

    expired_tenants = TenantApplication.objects.filter(
        expiration_date__lt=current_date, 
        status='active'
    )

    # Suspend the expired tenants
    for tenant in expired_tenants:
        tenant.status = 'suspended'
        tenant.save()
