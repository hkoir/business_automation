
from django.urls import path
from .import views
from .views import mark_notification_read_view

app_name = 'reporting'



urlpatterns = [
    
  path('report_dashboard/', views.report_dashboard, name='report_dashboard'),
  path('notification/read/<int:notification_id>/', mark_notification_read_view, name='mark_notification_read'),

  path('product_list/', views.product_list, name='product_list'),
  path('product_report/<int:product_id>/', views.product_report, name='product_report'),
  path('', views.warehouse_report, name='warehouse_report'),


  path('generate_sale_challan/<int:order_id>/', views.generate_sale_challan, name='generate_sale_challan'),
  path('download_sale_delivery_orders/<int:order_id>/', views.download_sale_delivery_order_csv, name='download_sale_delivery_orders'),


  path('generate_purchase_challan/<int:order_id>/', views.generate_purchase_challan, name='generate_purchase_challan'),
  path('download_purchase_delivery_orders/<int:order_id>/', views.download_purchase_delivery_order_csv, name='download_purchase_delivery_orders'),

]
