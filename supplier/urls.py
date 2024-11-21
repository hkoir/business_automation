
from django.urls import path
from .import views


app_name = 'supplier'


urlpatterns = [
    
  path('create_supplier/', views.create_supplier, name='create_supplier'),
  
  path('create_location/', views.create_location, name='create_location'),
  path('update_location/<int:location_id>/', views.update_location, name='update_location'),
  path('delete_location/<int:location_id>/', views.delete_location, name='delete_location'),    

  path('supplier_performance_list/', views.supplier_performance_list, name='supplier_performance_list'),
  path('create_performance/', views.add_or_update_performance, name='create_performance'),
  path('update_performance/<int:performance_id>/', views.add_or_update_performance, name='update_performance'),

  path('supplier_dashboard/', views.supplier_dashboard, name='supplier_dashboard'),
]
