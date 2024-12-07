from django.shortcuts import redirect
from django_tenants.utils import get_tenant_model
from django.http import Http404
import logging

logger = logging.getLogger(__name__)
from django.utils import timezone
from django_tenants.utils import get_public_schema_name


class TenantValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        subdomain = request.get_host().split('.')[0]
        tenant = getattr(request, 'tenant', None)
        
        if not tenant:           
            TenantModel = get_tenant_model()
            try:
                tenant = TenantModel.objects.get(domain_url=subdomain)  
                request.tenant = tenant
            except TenantModel.DoesNotExist:               
                if subdomain.startswith('company-'):
                    
                    logger.info(f"Unregistered tenant {subdomain} accessed. Redirecting to registration.")
                    return redirect('/apply_for_tenant/')  
                else:
                    
                    logger.error(f"Unknown subdomain {subdomain} detected. Tenant not found.")
                    raise Http404("No tenant associated with this subdomain.") 
        return self.get_response(request)




class TenantStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = getattr(request, 'tenant', None)  

        if tenant:
            tenant_instance = tenant.tenant.first() 
            if tenant_instance and tenant_instance.status == 'suspended':
                # messages.error(request, 'Your subscription has expired. Please renew to continue.')
                return redirect('clients:renew_tenant')  

        return self.get_response(request)



class RestrictPublicTenantAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            if hasattr(request, 'tenant') and request.tenant.schema_name == get_public_schema_name():                
                return redirect('/')       
        return self.get_response(request)
