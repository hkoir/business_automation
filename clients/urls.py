
from django.urls import path
from .import views


app_name = 'clients'

urlpatterns = [

    path('', views.tenant_dashboard, name='dashboard'),
    path('clients/apply_for_tenant/', views.apply_for_tenant_subscription, name='apply_for_tenant'),
    path('thanks/', views.thanks_for_application, name='thanks_for_application'),
    path('tenant_expire_check/', views.tenant_expire_check, name='tenant_expire_check'), 

    path('save_payment_info/<int:plan_id>/', views.save_payment_info, name='save_payment_info'), 
    path('renew_subscription/', views.renew_subscription, name='renew_subscription'), 

    path('create_user_profile/', views.create_user_profile, name='create_user_profile'), 


    
   
]