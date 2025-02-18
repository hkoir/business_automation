from django.shortcuts import redirect
from django_tenants.utils import get_tenant_model
from django.http import Http404
import logging

logger = logging.getLogger(__name__)
from django.utils import timezone
from django_tenants.utils import get_public_schema_name
from django.contrib import messages

from django.utils.deprecation import MiddlewareMixin
from django.db import connection
from django.http import HttpResponseForbidden
from django.urls import resolve
from django.contrib.auth import logout
from django.conf import settings


class TenantSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if hasattr(connection, 'schema_name'):
            schema_name = connection.schema_name
            request.session.cookie_name = f'sessionid_{schema_name}'


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
                if subdomain.startswith('demo-'):
                    
                    logger.info(f"Unregistered tenant {subdomain} accessed. Redirecting to registration.")
                    return redirect('/apply_for_tenant/')  
                else:
                    
                    logger.error(f"Unknown subdomain {subdomain} detected. Tenant not found.")
                    raise Http404("No tenant associated with this subdomain.") 
        return self.get_response(request)




class CustomGeneralPurposeMiddleWare:    
    TENANT_APPS = ['customer','accounts','core','finance','inventory','logistics','manufacture','operations','product','purchase','repairreturn','reporting','sales','supplier','shipment','tasks','transport'] 
    def __init__(self, get_response):
        self.get_response = get_response
        self.restricted_apps = ['purchase']

    def __call__(self, request):

        current_schema=request.tenant.schema_name == get_public_schema_name()
        if request.tenant.schema_name == get_public_schema_name() and request.user.is_authenticated:
            logout(request)
            request.session.flush()


        tenant = getattr(request, 'tenant', None) 

        if request.user.is_authenticated:     
            view_name = resolve(request.path_info).app_name       
            if request.user.groups.filter(name='Customer').exists() and view_name in self.restricted_apps:
                return HttpResponseForbidden("You are not allowed to access this page.")
            elif request.user.groups.filter(name='job_seekers').exists() and view_name in self.restricted_apps:
                return HttpResponseForbidden("You are not allowed to access this page.")
       

        if tenant.tenant.first():
            if tenant and tenant.tenant.first().subscription:
                if tenant and tenant.tenant.first().subscription.is_expired:
                    messages.error(request, "Your subscription has expired. Please renew to continue.")
                    return redirect('clients:dashboard') 
            else:
                messages.error(request, "No subscription plan")

        if request.user.is_authenticated and hasattr(request, 'tenant'):
            current_tenant = request.tenant
            if hasattr(request.user, 'tenant') and request.user.tenant != current_tenant:               
                messages.error(request, "You are not allowed to log in to this tenant.")
                return redirect('clients:dashboard') 
           

        if request.path.startswith('/admin/'):
            if hasattr(request, 'tenant') and request.tenant.schema_name == get_public_schema_name():   
                messages.error(request, "You are not authorized to access this page.")              
                return redirect('clients:dashboard')   
        
            
        # if current_schema and any(app in request.path for app in self.TENANT_APPS): 
        #     messages.warning(request, "You are not authorized to access this page.Please login with your credentials")          
        #     return redirect('accounts:login')      
        
        if tenant:   
            if tenant.tenant:  
                tenant_instance = tenant.tenant.first()
                if tenant_instance and tenant_instance.subscription.status == 'suspended':
                    messages.error(request, 'Your subscription has expired. Please renew to continue.')
                    return redirect('clients:apply_for_tenant')
            else:
                messages.error(request, 'No tenant found for this user.')
        else:
            return redirect('clients:dashboard') 
            # return redirect('clients:apply_for_tenant')  

        return self.get_response(request)
