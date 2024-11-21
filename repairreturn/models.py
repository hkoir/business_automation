from django.db import models

from accounts.models import User
from product.models import Product
from customer.models import Customer
from inventory.models import Warehouse,Location,Inventory

from sales.models import SaleOrder,SaleOrderItem
from purchase.models import PurchaseOrder,PurchaseOrderItem


class ReturnOrRefund(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True, blank=True, related_name='return_or_refund_user')
    sale = models.ForeignKey(SaleOrderItem,null=True, blank=True, related_name='sale_returns', on_delete=models.CASCADE)

    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True,blank=True)
    customer = models.ForeignKey(Customer, related_name='customer_return_refund', on_delete=models.CASCADE,null=True,blank=True)
    warehouse = models.ForeignKey(Warehouse, related_name='return_refund_warehouses', on_delete=models.CASCADE,null=True,blank=True)
    location = models.ForeignKey(Location, related_name='return_refund_locations', on_delete=models.CASCADE,null=True,blank=True)
    quantity_sold = models.PositiveIntegerField(null=True, blank=True)
    
    return_reason = models.CharField(max_length=20, choices=[
        ('DEFECTIVE', 'DEFECTIVE'),
        ('NOT_AS_DESCRIBED', 'NOT AS DESCRIBED'),
        ('OTHER', 'OTHER'),
    ],null=True, blank=True,)
    refund_type = models.CharField(max_length=20, choices=[
        ('FULL', 'Full Refund'),
        ('PARTIAL', 'Partial Refund'),
    ],null=True, blank=True,)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'PENDING'),
        ('Acknowledged', 'Acknowledged'),
        ('REJECTED', 'REJECTED'),
    ], default='PENDING',null=True, blank=True,)
   
    quantity_refund = models.PositiveIntegerField(null=True, blank=True)
    requested_date = models.DateTimeField(auto_now_add=True,null=True)
    processed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    processed_date = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.warehouse and self.sale.warehouse:
            self.warehouse = self.sale.warehouse
        if not self.location and self.sale.location:
            self.location = self.sale.location
        if not self.product and self.sale.product:
            self.product= self.sale.product
        if not self.quantity_sold and self.sale.quantity:
            self.quantity_sold = self.sale.quantity

        super().save(*args,**kwargs)

    def __str__(self):
        return f"{self.quantity_refund} nos {self.sale.product.name} refund applied by customer"


class FaultyProduct(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True, blank=True,related_name='user_faulty_product')
    return_request = models.ForeignKey(ReturnOrRefund, on_delete=models.CASCADE, related_name='faulty_products', null=True, blank=True,)
    
    sale = models.ForeignKey(SaleOrderItem, on_delete=models.CASCADE, related_name='faulty_sales')   
    warehouse = models.ForeignKey(Warehouse, related_name='return_warehouses', on_delete=models.CASCADE,null=True,blank=True)
    location = models.ForeignKey(Location, related_name='return_locations', on_delete=models.CASCADE,null=True,blank=True) 
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True, blank=True,)
    faulty_product_quantity = models.PositiveIntegerField(null=True, blank=True,)


    reason_for_fault = models.TextField(null=True, blank=True,)
    status = models.CharField(max_length=100, choices=[
        ('UNDER_INSPECTION', 'UNDER INSPECTION'), 
        ('REPAIRABLE', 'REPAIRABLE'), 
        ('UNREPAIRABLE', 'UNREPAIRABLE'),
        ('REPAIRED_AND_READY', 'REPAIRED_AND_READY'),
        ('REPAIRED_AND_RETURNED','REPAIRED_AND_RETURNED'),
        ('SCRAPPED', 'SCRAPPED')
    ], default='UNDER_INSPECTION',null=True, blank=True,)
    
    return_status = models.BooleanField(default=False,null=True, blank=True,) 
    repair_quantity = models.PositiveIntegerField(null=True, blank=True)
    return_quantity = models.PositiveIntegerField(null=True, blank=True)
    inspected_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    resolution_date = models.DateTimeField(null=True, blank=True)
    resolution_action = models.CharField(max_length=50, null=True, blank=True)
    customer_feedback = models.TextField(null=True, blank=True)
    inspection_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.return_request:
            if not self.product and self.return_request.sale:
                self.product = self.return_request.sale.product
            if not self.faulty_product_quantity:
                self.faulty_product_quantity = self.return_request.quantity_refund
            if not self.warehouse and self.return_request.warehouse:
                self.warehouse = self.return_request.warehouse
            if not self.location and self.return_request.location:
                self.location = self.return_request.location

        super().save(*args, **kwargs)

    def __str__(self):
        return f" {self.faulty_product_quantity} nos faulty {self.sale.product.name} issue raised by customer"



from inventory.models import InventoryTransaction

class Replacement(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    source_inventory = models.ForeignKey(Inventory,on_delete=models.CASCADE,related_name='replacement_source_inventory',null=True, blank=True,)    
    faulty_product = models.ForeignKey(FaultyProduct, on_delete=models.CASCADE, related_name='faulty_replacement')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='replacement_users', null=True, blank=True)

    warehouse=models.ForeignKey(Warehouse,on_delete=models.CASCADE,related_name='replacement_warehouse',null=True, blank=True,)
    location=models.ForeignKey(Location,on_delete=models.CASCADE,related_name='replacement_location',null=True, blank=True,)
   
    replacement_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='replacement_products', null=True, blank=True)  
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='replacement_customers', null=True, blank=True)
    transaction_type = models.CharField(max_length=20, choices=[
        ('INBOUND', 'Inbound'),
        ('OUTBOUND', 'Outbound'),
    ],null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'PENDING'),
        ('REPLACED_DONE', 'REPLACED_DONE'),
        ('CANCELLED', 'CANCELLED'),
    ], default='PENDING',null=True, blank=True,)

    feedback = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    def save(self, *args, **kwargs):

        if self.faulty_product and not self.replacement_product:
            self.replacement_product = self.faulty_product.product

        if self.faulty_product and self.faulty_product.return_request:
            sale = self.faulty_product.return_request.sale
            if sale and not self.customer:
                self.customer = sale.sale_order.customer

        if self.source_inventory:
            if not self.warehouse:
                self.warehouse = self.source_inventory.warehouse
            if not self.location:
                self.location = self.source_inventory.location
        super().save(*args, **kwargs)

        # Create InventoryTransaction for replacement OUT (OUTBOUND)
        if self.transaction_type == 'OUTBOUND':
            InventoryTransaction.objects.create(
                product=self.product,
                warehouse=self.warehouse,
                quantity=self.quantity,
                transaction_type='OUTBOUND',
                remarks=self.remarks
            )
        
        # Create InventoryTransaction for replacement IN (INBOUND)
        elif self.transaction_type == 'INBOUND':
            InventoryTransaction.objects.create(
                product=self.product,
                warehouse=self.warehouse,
                quantity=self.quantity,
                transaction_type='INBOUND',
                remarks=self.remarks
            )
        
        return super().save(*args, **kwargs)
    
       
    def __str__(self):
        return f"Replacement for {self.faulty_product.product.name} in {self.warehouse.name}"