
from django.urls import path
from .import views


app_name = 'customer'


urlpatterns = [ 
  
  path('create_customer/', views.create_customer, name='create_customer'),
  
  path('create_location/', views.create_location, name='create_location'),
  path('update_location/<int:location_id>/', views.update_location, name='update_location'),
  path('delete_location/<int:location_id>/', views.delete_location, name='delete_location'),

  path('customer_performance_list/', views.customer_performance_list, name='customer_performance_list'),
  path('create_performance/', views.add_or_update_performance, name='create_performance'),
  path('update_performance/<int:performance_id>/', views.add_or_update_performance, name='update_performance'),
  
  path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'),
 
]
