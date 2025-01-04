
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from .models import Client
from django.contrib.auth import login, logout, authenticate

from django.contrib import messages
from .forms import TenantApplicationForm

from .models import TenantInfo,TenantData,Client
from django.utils import timezone

import requests
from django.conf import settings
from django.http import JsonResponse
from django.core.management.base import BaseCommand




@login_required(login_url='accounts:login')
def tenant_dashboard(request):
    tenant = get_object_or_404(Client, schema_name=request.tenant.schema_name)
    if tenant.name == "demo1-1":
        template_name = "tenant/tenant_1_dashboard.html"
        context = {"tenant": tenant, "welcome_message": "Welcome to Company 1's Dashboard"}
    elif tenant.name == "demo2-2":
        template_name = "tenant/tenant_2_dashboard.html"
        context = {"tenant": tenant, "custom_reports": True}
    else:
        template_name = "tenant/default_dashboard.html"
        context = {"tenant": tenant}

    return render(request, template_name, context)




def tenant_expire_check(request):
    tenant = getattr(request, 'tenant', None)   
    if tenant:
        tenant_instance = tenant.tenant.first() 
        if tenant_instance and tenant_instance.expiration_date:
            if tenant_instance.expiration_date < timezone.now().date():
                return redirect('clients:renew_tenant')
            else:
               return redirect('core:dashboard')
    return redirect('core:dashboard')



def apply_for_tenant(request):
    if request.method == 'POST':
        form = TenantApplicationForm(request.POST)
        if form.is_valid():
            form.save()  
            messages.success(request, 'Your application has been submitted successfully. We will review it shortly.')
            return redirect('clients:dashboard') 
    else:
        form = TenantApplicationForm()
    return render(request, 'tenant/apply_for_tenant.html', {'form': form})



def process_payment(amount, order_id):
    
    sslcommerz_url = 'https://sandbox.sslcommerz.com/gwprocess/v4/api.php'
    
    payload = {
        'store_id': 'your_store_id', 
        'store_password': 'your_store_password',  
        'total_amount': amount,
        'currency': 'BDT',
        'tran_id': order_id,
        'success_url': 'http://yourdomain.com/payment/success/',
        'fail_url': 'http://yourdomain.com/payment/fail/',
        'cancel_url': 'http://yourdomain.com/payment/cancel/',
        'cus_name': 'Customer Name',  
        'cus_email': 'customer@example.com',  
        'cus_add1': 'Address',
        'cus_city': 'City',
        'cus_country': 'Bangladesh',
        'cus_phone': '0123456789',
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    response = requests.post(sslcommerz_url, data=payload, headers=headers)
    response_data = response.json()

    if response_data['status'] == 'SUCCESS':
        return response_data['GatewayPageURL']  # Return the redirect URL for the payment gateway
    else:
        return None
    


def renew_tenant(request):
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        return redirect('/')

    tenant_instance = tenant.tenant.first()
    if not tenant_instance:
        return redirect('/')

    if request.method == 'POST':
        extension_period = int(request.POST.get('extension_period'))  # In days
        amount = 1000  # Price in BDT (Bangladeshi Taka)
        order_id = f'tenant-renew-{timezone.now().strftime("%Y%m%d%H%M%S")}'  # Unique order ID

        payment_url = process_payment(amount, order_id)

        if payment_url:
            return redirect(payment_url)  # Redirect to SSLCOMMERZ payment page
        else:
            return render(request, 'tenant/renew_tenant.html', {
                'tenant': tenant_instance,
                'error_message': 'Payment initialization failed. Please try again.',
            })

    return render(request, 'tenant/renew_tenant.html', {'tenant': tenant_instance})




class Command(BaseCommand):
    help = 'Suspends tenants whose subscription has expired'

    def handle(self, *args, **kwargs):
        current_date = timezone.now().date()

        expired_tenants = TenantData.objects.filter(
            expiration_date__lt=current_date, 
            status='active'
        )

        # Suspend expired tenants
        for tenant in expired_tenants:
            tenant.status = 'suspended'
            tenant.save()
            self.stdout.write(self.style.SUCCESS(f"Suspended tenant: {tenant.name}"))



def thanks_for_application(request):
    rules = TenantInfo.objects.filter(name="Rules and Regulations").first()
    guidelines = TenantInfo.objects.filter(name="Branding Guidelines").first()

    return render(request, 'tenant/thanks_for_application.html', {
        'rules': rules,
        'guidelines': guidelines,
    })


