from django.db import models
from django.db.models import F,Q,Sum,Case, When
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.models import User

import logging
logger = logging.getLogger(__name__)
from django import forms

from product.models import Product,Category
from core.models import Employee
from finance.models import PurchaseInvoice,SaleInvoice
from logistics.models import PurchaseShipment,SaleShipment
from repairreturn.models import Replacement,ReturnOrRefund,FaultyProduct  
from manufacture.models import MaterialsRequestOrder
from operations.models import OperationsRequestOrder,ExistingOrder
from purchase.models import PurchaseOrder, PurchaseRequestOrder
from inventory.models import InventoryTransaction,Warehouse,TransferOrder
from sales.models import SaleOrder,SaleRequestOrder
from reporting.models import Notification




def create_notification(user, message):   
    Notification.objects.create(user=user, message=message)
    

def mark_notification_as_read(notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()
    except Notification.DoesNotExist:
        pass  




# for purchase update ######################################################################
def update_purchase_order(purchase_order_id):
    try:
        with transaction.atomic():
            purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)         
            print(f"Updating Purchase Order ID: {purchase_order_id}")
            
            shipments = purchase_order.purchase_shipment.all()
            
            if shipments.exists(): 
                all_shipments_delivered = (
                    shipments.filter(status='DELIVERED').count()
                    == shipments.count()
                )
                if all_shipments_delivered:
                    print("All shipments delivered. Updating status to DELIVERED.")
                    purchase_order.status = 'DELIVERED'
                    purchase_order.save()
                else:
                    print("Not all shipments delivered. Status remains unchanged.")
            else:
                print("No shipments found for this purchase order. Status remains unchanged.")
    except Exception as e:
        print(f"Error updating purchase order {purchase_order_id}: {e}")



def update_purchase_request_order(request_order_id):
    try:
        with transaction.atomic():
            request_order = PurchaseRequestOrder.objects.get(id=request_order_id)
            total_requested_product = request_order.purchase_request_order.aggregate(total_requested_product=Sum('quantity'))['total_requested_product'] or 0

            total_dispatch_quantity = 0

            for purchase_order in request_order.purchase_order_request_order.all():
                for shipment in purchase_order.purchase_shipment.all():
                    dispatch_sum = shipment.shipment_dispatch_item.aggregate(total_dispatch=Sum('dispatch_quantity'))['total_dispatch'] or 0
                    total_dispatch_quantity += dispatch_sum

            if total_dispatch_quantity == total_requested_product:
                request_order.status = 'DELIVERED'
            elif 0 < total_dispatch_quantity < total_requested_product:
                request_order.status = 'PARTIAL_DELIVERED'
            elif total_dispatch_quantity == 0:
                request_order.status = 'IN_PROCESS'

            request_order.save()

    except Exception as e:
        print(f"Error updating sale request order: {e}")
       
    


def update_shipment_status(shipment_id):
    try:
        shipment = PurchaseShipment.objects.get(id=shipment_id)
        all_items_delivered = shipment.shipment_dispatch_item.filter(status='DELIVERED').count() == shipment.shipment_dispatch_item.count()
        if all_items_delivered:
            shipment.status = 'DELIVERED'
            shipment.save()
            logger.info(f"Shipment {shipment_id} marked as DELIVERED.")
    except PurchaseShipment.DoesNotExist:
        logger.error(f"Shipment {shipment_id} not found.")



# for sale update ########################################################################

def update_sale_order(sale_order_id):
    sale_order = SaleOrder.objects.get(id=sale_order_id)
    all_shipments_delivered = sale_order.sale_shipment.filter(status='DELIVERED').count() == sale_order.sale_shipment.count()
    if all_shipments_delivered:
        sale_order.status = 'DELIVERED'       
        sale_order.save()      



def update_sale_request_order(request_order_id):
    try:
        with transaction.atomic():
            request_order = SaleRequestOrder.objects.get(id=request_order_id)
            total_requested_product = request_order.sale_request_order.aggregate(total_requested_product=Sum('quantity'))['total_requested_product'] or 0

            total_dispatch_quantity = 0
            for sale_order in request_order.sale_request.all():
                for shipment in sale_order.sale_shipment.all():
                    dispatch_sum = shipment.sale_shipment_dispatch.aggregate(total_dispatch=Sum('dispatch_quantity'))['total_dispatch'] or 0
                    total_dispatch_quantity += dispatch_sum

            if total_dispatch_quantity == total_requested_product:
                request_order.status = 'DELIVERED'
            elif 0 < total_dispatch_quantity < total_requested_product:
                request_order.status = 'PARTIAL_DELIVERED'
            elif total_dispatch_quantity == 0:
                request_order.status = 'IN_PROCESS'

            request_order.save()
            
    except Exception as e:
        print(f"Error updating sale request order: {e}")

    

def update_sale_shipment_status(shipment_id):
    shipment = SaleShipment.objects.get(id=shipment_id)
    all_items_delivered = shipment.sale_shipment_dispatch.filter(status='DELIVERED').count() == shipment.sale_shipment_dispatch.count()
    if all_items_delivered:
        shipment.status = 'DELIVERED'
        shipment.save()

############################################################################


def assign_roles(order, requester, reviewer, approver):
    order.requester = requester
    order.reviewer = reviewer
    order.approver = approver
    order.save()  




def get_warehouse_stock(warehouse, product):
    transactions = InventoryTransaction.objects.filter(
        warehouse=warehouse, product=product
    ).values('transaction_type').annotate(total=Sum('quantity'))

    inbound = sum(t['total'] for t in transactions if t['transaction_type'] in ['INBOUND', 'TRANSFER_IN','MANUFACTURE','REPLACEMENT_IN','EXISTING_ITEM_IN'])
    outbound = sum(t['total'] for t in transactions if t['transaction_type'] in ['OUTBOUND', 'TRANSFER_OUT','REPLACEMENT_OUT'])

    return inbound - outbound



def calculate_stock_value(product, warehouse): 
    total_purchase = InventoryTransaction.objects.filter(
        product=product,
        warehouse=warehouse, 
        transaction_type='INBOUND',
        purchase_order__isnull=False
    ).aggregate(total=Sum('quantity'))['total'] or 0

    total_manufacture = InventoryTransaction.objects.filter(
        product=product,
        warehouse=warehouse,  
        transaction_type='MANUFACTURE',
        manufacture_order__isnull=False
    ).aggregate(total=Sum('quantity'))['total'] or 0

    total_sold = InventoryTransaction.objects.filter(
        product=product,
        warehouse=warehouse,  
        transaction_type='OUTBOUND',
        sales_order__isnull=False
    ).exclude(
        Q(remarks__icontains='transfer') |
        Q(remarks__icontains='replacement')
    ).aggregate(total=Sum('quantity'))['total'] or 0


    total_replacement_out = InventoryTransaction.objects.filter(
        product=product,
        warehouse=warehouse,  
        transaction_type='REPLACEMENT_OUT',  
    ).aggregate(total=Sum('quantity'))['total'] or 0

    total_transfer_in = InventoryTransaction.objects.filter(
        product=product,
        warehouse=warehouse,
        transaction_type='TRANSFER_IN',  
    ).aggregate(total=Sum('quantity'))['total'] or 0


    total_transfer_out = InventoryTransaction.objects.filter(
        product=product,
        warehouse=warehouse,
        transaction_type='TRANSFER_OUT', 
    ).aggregate(total=Sum('quantity'))['total'] or 0

    total_Existing_in = InventoryTransaction.objects.filter(
        product=product,
        warehouse=warehouse,
        transaction_type='EXISTING_ITEM_IN', 
    ).aggregate(total=Sum('quantity'))['total'] or 0
    total_operations_out = InventoryTransaction.objects.filter(
        product=product,
        warehouse=warehouse,
        transaction_type='OPERATIONS_OUT', 
    ).aggregate(total=Sum('quantity'))['total'] or 0


    total_available = (
        total_purchase + total_manufacture + total_transfer_in + total_Existing_in
        - (total_sold + total_transfer_out + total_replacement_out + total_operations_out)
    )   
    total_stock = total_purchase + total_manufacture + total_transfer_in + total_Existing_in

    if total_available < 0:
        logger.warning(f"Negative stock detected for {product.name} in {warehouse.name}.")
        total_available = 0 

    return {
        'total_purchase': total_purchase,
        'total_manufacture': total_manufacture,
        'total_existing_in': total_Existing_in,
        'total_operations_out': total_operations_out,
        'total_sold': total_sold,
        'total_replacement_out': total_replacement_out,
        'total_transfer_in': total_transfer_in,
        'total_transfer_out': total_transfer_out,
        'total_available': total_available,
        'total_stock':total_stock
    }




def calculate_stock_value2(product, warehouse=None): 
    filters = {'product': product}
    if warehouse:
        if isinstance(warehouse, Warehouse):  
            filters['warehouse'] = warehouse
        else:
            logger.error("Invalid warehouse instance provided.")
            raise ValueError("Invalid warehouse instance provided.")


    total_purchase = InventoryTransaction.objects.filter(
        transaction_type='INBOUND',
        purchase_order__isnull=False,
        **filters
    ).aggregate(total=Sum('quantity'))['total'] or 0

    total_manufacture = InventoryTransaction.objects.filter(
        transaction_type='MANUFACTURE',
        manufacture_order__isnull=False,
        **filters
    ).aggregate(total=Sum('quantity'))['total'] or 0

    total_sold = InventoryTransaction.objects.filter(
        transaction_type='OUTBOUND',
        sales_order__isnull=False,
        **filters
    ).exclude(
        Q(remarks__icontains='transfer') |
        Q(remarks__icontains='replacement')
    ).aggregate(total=Sum('quantity'))['total'] or 0

    total_replacement_out = InventoryTransaction.objects.filter(
        transaction_type='REPLACEMENT_OUT',
        **filters
    ).aggregate(total=Sum('quantity'))['total'] or 0

    total_transfer_in = InventoryTransaction.objects.filter(
        transaction_type='TRANSFER_IN',
        **filters
    ).aggregate(total=Sum('quantity'))['total'] or 0

    total_transfer_out = InventoryTransaction.objects.filter(
        transaction_type='TRANSFER_OUT',
        **filters
    ).aggregate(total=Sum('quantity'))['total'] or 0

    total_existing_in = InventoryTransaction.objects.filter(
        transaction_type='EXISTING_ITEM_IN',
        **filters
    ).aggregate(total=Sum('quantity'))['total'] or 0

    total_operations_out = InventoryTransaction.objects.filter(
        transaction_type='OPERATIONS_OUT',
        **filters
    ).aggregate(total=Sum('quantity'))['total'] or 0

    total_available = (
        total_purchase + total_manufacture + total_transfer_in + total_existing_in
        - (total_sold + total_transfer_out + total_replacement_out + total_operations_out)
    )

    total_stock = total_purchase + total_manufacture + total_transfer_in + total_existing_in

    if total_available < 0:
        logger.warning(
            f"Negative stock detected for {product.name} in "
            f"{warehouse.name if warehouse else 'all warehouses'}"
        )
        total_available = 0

    return {
        'total_purchase': total_purchase,
        'total_manufacture': total_manufacture,
        'total_existing_in': total_existing_in,
        'total_operations_out': total_operations_out,
        'total_sold': total_sold,
        'total_replacement_out': total_replacement_out,
        'total_transfer_in': total_transfer_in,
        'total_transfer_out': total_transfer_out,
        'total_available': total_available,
        'total_stock': total_stock
    }




class CommonFilterForm(forms.Form):
    start_date = forms.DateField(
        label='Start Date',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    end_date = forms.DateField(
        label='End Date',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    days = forms.IntegerField(
        label='Number of Days',
        min_value=1,
        required=False
    )

 
    ID_number = forms.CharField(
        label='Order ID',
        required=False,
       
    )   

    warehouse_name = forms.ModelChoiceField(queryset=Warehouse.objects.all(),required=False)
    product_name = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_product_name'}),
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_category'}),
    )

    employee_name = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_employee_name'}),
    )
           
    purchase_request_order_id = forms.ModelChoiceField(
        queryset=PurchaseRequestOrder.objects.all(),
        required=False,        
        widget=forms.Select(attrs={'id': 'id_purchase_request_order_id'}),)
    
    purchase_order_id = forms.ModelChoiceField(
        queryset=PurchaseOrder.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_purchase_order_id'}),)
    
    purchase_shipment_id = forms.ModelChoiceField(
        queryset=PurchaseShipment.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_purchase_shipment_id'}),)
    
    purchase_invoice_id = forms.ModelChoiceField(
        queryset=PurchaseInvoice.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_purchase_invoice_id'}),)
    

    sale_request_order_id = forms.ModelChoiceField(
        queryset=SaleRequestOrder.objects.all(),
        required=False,        
        widget=forms.Select(attrs={'id': 'id_sale_request_order_id'}),)
    
    sale_order_id = forms.ModelChoiceField(
        queryset=SaleOrder.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_sale_order_id'}),)
    
    
    sale_shipment_id = forms.ModelChoiceField(
        queryset=SaleShipment.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_sale_shipment_id'}),)
    
    sale_invoice_id = forms.ModelChoiceField(
        queryset=SaleInvoice.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_sale_invoice_id'}),)
    
    transfer_id = forms.ModelChoiceField(
        queryset=TransferOrder.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_transfer_id'}),)
    
    return_refund__id = forms.ModelChoiceField(
        queryset=ReturnOrRefund.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_return_id'}),)
    
    materials_order_id = forms.ModelChoiceField(
        queryset=MaterialsRequestOrder.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_materials_order_id'}),)
   
    operations_request_order_id = forms.ModelChoiceField(
        queryset=OperationsRequestOrder.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_operations_request_order_id'}),)
   










