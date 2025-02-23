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


from django.urls import Resolver404

class CustomGeneralPurposeMiddleWare2:    
    TENANT_APPS = ['customer','core','finance','inventory','logistics','manufacture','operations','product','purchase','repairreturn','reporting','sales','supplier','shipment','tasks','transport'] 
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
            try:
                view_name = resolve(request.path_info).app_name
                if request.user.groups.filter(name__in=('partner', 'job_seeker', 'public')).exists() and view_name in self.restricted_apps:
                    return HttpResponseForbidden("You are not allowed to access this page.")
            except Resolver404:
                view_name = None
        

        if request.user.is_authenticated and hasattr(request, 'tenant'):
            current_tenant = request.tenant
            if hasattr(request.user, 'tenant') and request.user.tenant != current_tenant:               
                messages.error(request, "You are not allowed to log in to this tenant.")
                return redirect('clients:tenant_expire_check')       
        
        if tenant:
            tenant_instance = tenant.tenant.first()  # Gets the first related Tenant (if any)
            if tenant_instance:
                subscription = getattr(tenant_instance, 'subscription', None)
                if subscription:
                    if subscription.is_expired:
                        messages.error(request, "Your subscription has expired. Please renew to continue.")
                        return redirect('clients:tenant_expire_check')
                else:
                    messages.error(request, "No subscription plan found.")
            else:
                messages.error(request, "No tenant instance found.")

               

        return self.get_response(request)



class CustomGeneralPurposeMiddleWare:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = getattr(request, 'tenant', None)
        is_public_tenant = tenant and tenant.schema_name == get_public_schema_name()

        # Allow public schema login without tenant checks
        if is_public_tenant:
            return self.get_response(request)

        # Check if tenant user is on their correct tenant domain
        if request.user.is_authenticated and tenant:
            user_tenant = getattr(request.user, 'tenant', None)
            if user_tenant and user_tenant.schema_name != tenant.schema_name:
                logout(request)
                messages.error(request, "You are not allowed to log in to this tenant.")
                return redirect('login')

        return self.get_response(request)
    




from django.contrib.auth import get_user_model
from accounts.models import UserProfile  
User = get_user_model() 





class CustomTenantAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if hasattr(connection, 'schema_name'):
            schema_name = connection.schema_name
            request.session.cookie_name = f'sessionid_{schema_name}'

        user = request.user
        if user.is_authenticated: 
            if user.is_superuser:
                return

            try:
                user_profile = UserProfile.objects.get(user=user)
                current_tenant = request.tenant
       
                if user_profile.tenant != current_tenant:
                    logout(request)
                    if user_profile.tenant:
                        return redirect(f'http://{user_profile.tenant.subdomain}.localhost:8000')
                 
                    return redirect('http://localhost:8000')

            except UserProfile.DoesNotExist:           
                logout(request)
                return redirect('http://localhost:8000')
