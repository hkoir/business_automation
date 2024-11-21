from reporting.models import Notification
from django.db import models
from django.db.models import Sum

from purchase.models import PurchaseOrder, PurchaseOrderItem
from logistics.models import PurchaseShipment
from purchase.models import PurchaseRequestOrder
from finance.models import PurchaseInvoice
from django.db.models import Sum, F, Case, When
from inventory.models import InventoryTransaction,Inventory

from django.db.models import F,Q
from repairreturn.models import Replacement
from inventory.models import TransferItem

from sales.models import SaleOrder,SaleRequestOrder
from logistics.models import SaleShipment
from django.db import transaction

import logging
logger = logging.getLogger(__name__)


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
    purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
    all_shipments_delivered = purchase_order.purchase_shipment.filter(status='DELIVERED').count() == purchase_order.purchase_shipment.count()
    if all_shipments_delivered:
        purchase_order.status = 'DELIVERED'       
        purchase_order.save()      


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

    inbound = sum(t['total'] for t in transactions if t['transaction_type'] in ['INBOUND', 'TRANSFER_IN','MANUFACTURE','REPLACEMENT_IN'])
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


    total_replacement = InventoryTransaction.objects.filter(
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

    total_available = (
        total_purchase + total_manufacture + total_transfer_in
        - (total_sold + total_transfer_out + total_replacement)
    )   
    total_stock = total_purchase + total_manufacture + total_transfer_in

    if total_available < 0:
        logger.warning(f"Negative stock detected for {product.name} in {warehouse.name}.")
        total_available = 0 

    return {
        'total_purchase': total_purchase,
        'total_manufacture': total_manufacture,
        'total_sold': total_sold,
        'total_replacement': total_replacement,
        'total_transfer_in': total_transfer_in,
        'total_transfer_out': total_transfer_out,
        'total_available': total_available,
        'total_stock':total_stock
    }






def calculate_stock_value2(product, warehouse=None):
    filters = {'product': product}

    if warehouse:
        filters['warehouse'] = warehouse  

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

    total_replacement = InventoryTransaction.objects.filter(
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

    total_available = (
        total_purchase + total_manufacture + total_transfer_in
        - (total_sold + total_transfer_out + total_replacement)
    )

 
    total_stock = total_purchase + total_manufacture + total_transfer_in

    if total_available < 0:
        logger.warning(f"Negative stock detected for {product.name} in {warehouse.name if warehouse else 'all warehouses'}")
        total_available = 0

    return {
        'total_purchase': total_purchase,
        'total_manufacture': total_manufacture,
        'total_sold': total_sold,
        'total_replacement': total_replacement,
        'total_transfer_in': total_transfer_in,
        'total_transfer_out': total_transfer_out,
        'total_available': total_available,
        'total_stock': total_stock
    }
