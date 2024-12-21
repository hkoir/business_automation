from django.shortcuts import redirect
from django_tenants.utils import get_tenant_model
from django.http import Http404
import logging

logger = logging.getLogger(__name__)
from django.utils import timezone
from django_tenants.utils import get_public_schema_name
from django.contrib import messages



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




class CustomGeneralPurposeMiddleWare:
    TENANT_APPS = ['customer','accounts','core','finance','inventory','logistics','manufacture','operations','product','purchase','repairreturn','reporting','sales','supplier','shipment','tasks'] 
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_schema=request.tenant.schema_name == get_public_schema_name()
        tenant = getattr(request, 'tenant', None) 


        if request.user.is_authenticated and hasattr(request, 'tenant'):
            current_tenant = request.tenant
            if hasattr(request.user, 'tenant') and request.user.tenant != current_tenant:               
                messages.error(request, "You are not allowed to log in to this tenant.")
                return redirect('accounts:login') 
           

        if request.path.startswith('/admin/'):
            if hasattr(request, 'tenant') and request.tenant.schema_name == get_public_schema_name():   
                messages.error(request, "You are not authorized to access this page.")              
                return redirect('/')   
            
        if current_schema and any(app in request.path for app in self.TENANT_APPS): 
            messages.error(request, "You are not authorized to access this page.")          
            return redirect('/')   
        
        if tenant:
            tenant_instance = tenant.tenant.first() 
            if tenant_instance and tenant_instance.status == 'suspended':
                messages.error(request, 'Your subscription has expired. Please renew to continue.')
                return redirect('clients:renew_tenant')               

        return self.get_response(request)

