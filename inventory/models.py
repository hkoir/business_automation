
from django.db import models
from product.models import Product
import uuid
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.apps import apps
from simple_history.models import HistoricalRecords

from sales.models import SaleOrder
from manufacture.models import ReceiveFinishedGoods
from purchase.models import PurchaseOrder




class Warehouse(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True, blank=True,related_name='warehouse_user')
    name = models.CharField(max_length=100)
    warehouse_id = models.CharField(max_length=150, unique=True, null=True, blank=True)  
    address = models.CharField(max_length=255, blank=True, null=True)
    city=models.CharField(max_length=100,null=True,blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.warehouse_id:
            self.warehouse_id = f"WH-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f" {self.name} at {self.locations.first()} "



class Location(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True, blank=True,related_name='location_user')
    location_id = models.CharField(max_length=150, unique=True, null=True, blank=True)     
    warehouse = models.ForeignKey(Warehouse, related_name='locations', on_delete=models.CASCADE)  
    address= models.TextField(null=True,blank=True)  
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.location_id:
            self.location_id = f"LOCID-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

import logging
logger = logging.getLogger(__name__)

from manufacture.models import MaterialsRequestOrder

class InventoryTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='inventory_transaction_user')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE,null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE,null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True, blank=True)
    transaction_type = models.CharField(
    max_length=20,
    choices=[
        ('INBOUND', 'Inbound'),
        ('OUTBOUND', 'Outbound'),
        ('MANUFACTURE', 'Manufacture'),
        ('REPLACEMENT_OUT', 'Replacement Out'),
        ('REPLACEMENT_IN', 'Replacement In'),
        ('TRANSFER_OUT', 'Transfer Out'),
        ('TRANSFER_IN', 'Transfer In'),
    ],
    null=True, blank=True
)

    
    quantity = models.PositiveIntegerField(null=True, blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)    
   
    purchase_order = models.ForeignKey(PurchaseOrder, related_name='purchase_transactions', null=True, blank=True, on_delete=models.CASCADE)
    sales_order = models.ForeignKey(SaleOrder, related_name='sale_transactions', null=True, blank=True, on_delete=models.CASCADE)
    manufacture_order = models.ForeignKey(MaterialsRequestOrder,related_name='manufacure_inventory',null=True,blank=True, on_delete=models.CASCADE)
    remarks = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def update_inventory(self):
        try:
            if self.quantity == 0:
                logger.info(f"Skipped inventory update: Zero quantity for {self.product.name}.")
                return True

            inventory, created = Inventory.objects.get_or_create(
                product=self.product, warehouse=self.warehouse,
                defaults={'quantity': 0}
            )
            if created:
                logger.info(f"Created new inventory record for {self.product.name} in {self.warehouse.name}")

            if self.transaction_type in ['OUTBOUND', 'TRANSFER_OUT', 'REPLACEMENT_OUT']:
                if inventory.quantity < self.quantity:
                    raise ValueError(
                        f"Insufficient stock for {self.product.name} in {self.warehouse.name}."
                    )
                inventory.quantity -= self.quantity

            elif self.transaction_type in ['INBOUND', 'MANUFACTURE', 'TRANSFER_IN']:
                inventory.quantity += self.quantity

            else:
                raise ValueError(f"Invalid transaction type: {self.transaction_type}")

            inventory.save()

            logger.info(
                f"Updated inventory: {self.product.name}, Warehouse: {self.warehouse.name}, "
                f"Type: {self.transaction_type}, Quantity: {self.quantity}."
            )
            return True

        except ValueError as ve:
            logger.error(f"Inventory update failed: {ve}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating inventory: {e}")
            return False

    def clean(self):  
        selected_orders = [self.purchase_order, self.sales_order, self.manufacture_order]
        if sum(1 for order in selected_orders if order is not None) > 1:
            raise ValidationError("Only one of purchase_order, sales_order, or manufacture_order should be selected.")

    def __str__(self):       
        return f"{self.transaction_type} of {self.quantity} {self.product}"


class Inventory(models.Model):
    inventory_transaction = models.ForeignKey(
        InventoryTransaction,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='inventory_transaction'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='inventory_user'
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_inventories',
        null=True,
        blank=True
    )
    quantity = models.IntegerField(default=0,null=True,blank=True)  # Add this field for direct updates
    remarks = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.warehouse} - {self.product} available qty:{self.quantity}"




class TransferOrder(models.Model):
    order_number = models.CharField(max_length=20, unique=True)
    order_status = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='transfer_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.order_number
    

from django.db import transaction

class TransferItem(models.Model):
    transfer_order = models.ForeignKey(TransferOrder, related_name='transfers', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    source_warehouse = models.ForeignKey(Warehouse, related_name='source_transfers', on_delete=models.CASCADE, null=True, blank=True)
    target_warehouse = models.ForeignKey(Warehouse, related_name='target_transfers', on_delete=models.CASCADE, null=True, blank=True)
    source_location = models.ForeignKey(Location, related_name='source_locations', on_delete=models.CASCADE, null=True, blank=True)
    target_location = models.ForeignKey(Location, related_name='target_locations', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    remarks = models.TextField(null=True, blank=True)    

    def __str__(self):
        return f"{self.quantity} nos {self.product.name} transferred from {self.source_warehouse.name} to {self.target_warehouse.name}"



class ReorderLevel(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reorder_levels',null=True,blank=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='reorder_warehouse',null=True,blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='reorder_location',null=True,blank=True)
    reorder_level = models.PositiveIntegerField(null=True,blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True, blank=True,related_name='reorder_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reorder level for {self.product.product_name} - {self.warehouse.warehouse_name} is {self.reorder_level}"

    class Meta:
        unique_together = ('product', 'warehouse')  