from django.db import models

from product.models import Product
from inventory.models import Warehouse
from logistics.models import PurchaseShipment,SaleShipment
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from inventory.models import Location,Inventory



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  

    def __str__(self):
        return f"{self.message} - {'Read' if self.is_read else 'Unread'}"


class InventoryReport(models.Model):
    inventory=models.ForeignKey(Inventory,on_delete=models.CASCADE,related_name='inventory_report',null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='inventory_report_user')
    report_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Report for {self.inventory}"


class SaleShipmentReport(models.Model):
    sale_shipment = models.ForeignKey(SaleShipment, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='sale_shipment_report_user')
    report_date = models.DateField(auto_now_add=True)  
    total_dispatch = models.PositiveIntegerField(default=0)
    total_delivered = models.PositiveIntegerField(default=0)
    total_pending = models.PositiveIntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return f"Report for {self.sale_shipment.tracking_number}-{self.report_date}"


class PurchaseShipmentReport(models.Model):   
    purchase_shipment = models.ForeignKey(PurchaseShipment, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='purchase_shipment_report_user')
    report_date = models.DateField(auto_now_add=True)  
    total_dispatch = models.PositiveIntegerField(default=0)
    total_delivered = models.PositiveIntegerField(default=0)
    total_pending = models.PositiveIntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return f"Report for { self.purchase_shipment.tracking_number} on {self.report_date}"


