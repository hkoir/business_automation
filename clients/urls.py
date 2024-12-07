
from django.urls import path
from .import views


app_name = 'clients'

urlpatterns = [

    path('', views.tenant_dashboard, name='dashboard'),
    path('clients/apply_for_tenant/', views.apply_for_tenant, name='apply_for_tenant'),
    path('thanks/', views.thanks_for_application, name='thanks_for_application'),
    path('tenant_expire_check/', views.tenant_expire_check, name='tenant_expire_check'), 

    path('renew-tenant/', views.renew_tenant, name='renew_tenant'),
   
   
]