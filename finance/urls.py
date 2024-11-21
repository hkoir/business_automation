
from django.urls import path
from .import views


app_name = 'finance'



urlpatterns = [
    path('create_purchase_invoice/<int:order_id>/', views.create_purchase_invoice, name='create_purchase_invoice'),
    path('create_purchase_payment/<int:invoice_id>/', views.create_purchase_payment, name='create_purchase_payment'),
   
    path('purchase_invoice_list/', views.purchase_invoice_list, name='purchase_invoice_list'),
    path('purchase_invoice_detail/<int:invoice_id>/', views.purchase_invoice_detail, name='purchase_invoice_detail'),

    path('create_sale_invoice/<int:order_id>/', views.create_sale_invoice, name='create_sale_invoice'),
    path('create_sale_payment/<int:invoice_id>/', views.create_sale_payment, name='create_sale_payment'),
    path('sale_invoice_list/', views.sale_invoice_list, name='sale_invoice_list'),
    
    path('sale_invoice_detail/<int:invoice_id>/', views.sale_invoice_detail, name='sale_invoice_detail'),


]