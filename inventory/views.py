from django.shortcuts import render,redirect,get_object_or_404
from django.db.models import Sum, Avg,Count,Q,Case, When, IntegerField,F,Max,DurationField, DecimalField,FloatField
from django.db import transaction
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
import json
from itertools import groupby
from operator import itemgetter
from django.core.paginator import Paginator
from django.utils.timezone import now

from inventory.models import Product, InventoryTransaction
from manufacture.models import ManufactureQualityControl
from repairreturn.models import Replacement
from product.models import Product
from purchase.models import QualityControl
from sales.models import SaleQualityControl
from .models import Inventory,InventoryTransaction
from .models import InventoryTransaction, Inventory,Warehouse,Location
from .forms import QualityControlCompletionForm,InventoryTransactionForm,AddWarehouseForm,AddLocationForm
from .models import TransferItem,TransferOrder

from .forms import TransferProductForm
from operator import itemgetter

import logging
logger = logging.getLogger(__name__)


from utils import update_sale_shipment_status,update_sale_order,update_sale_request_order
from utils import get_warehouse_stock,calculate_stock_value,calculate_stock_value2
from utils import update_purchase_order,update_purchase_request_order,update_shipment_status

from core.forms import CommonFilterForm
from reporting.forms import SummaryReportChartForm
from django.utils import timezone
from datetime import timedelta




def inventory_dashboard(request):
    return render(request,'inventory/inventory_dashboard.html')



def manage_warehouse(request, id=None):
    if request.method == 'POST' and 'delete_id' in request.POST:
        instance = get_object_or_404(Warehouse, id=request.POST.get('delete_id'))
        instance.delete()
        messages.success(request, "Deleted successfully")
        return redirect('inventory:create_warehouse')

    instance = get_object_or_404(Warehouse, id=id) if id else None
    message_text = "updated successfully!" if id else "added successfully!"
    form = AddWarehouseForm(request.POST or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, message_text)
        return redirect('inventory:create_warehouse')

    datas = Warehouse.objects.all().order_by('-created_at')
    paginator = Paginator(datas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'inventory/manage_warehouse.html', {
        'form': form,
        'instance': instance,
        'datas': datas,
        'page_obj': page_obj
    })



def manage_location(request, id=None):
    if request.method == 'POST' and 'delete_id' in request.POST:
        instance = get_object_or_404(Location, id=request.POST.get('delete_id'))
        instance.delete()
        messages.success(request, "Deleted successfully")
        return redirect('inventory:create_location')

    instance = get_object_or_404(Location, id=id) if id else None
    message_text = "updated successfully!" if id else "added successfully!"
    form = AddLocationForm(request.POST or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, message_text)
        return redirect('inventory:create_location')

    datas = Location.objects.all().order_by('-created_at')
    paginator = Paginator(datas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'inventory/manage_location.html', {
        'form': form,
        'instance': instance,
        'datas': datas,
        'page_obj': page_obj
    })



def get_locations(request):
    warehouse_id = request.GET.get('warehouse_id')
    locations = Location.objects.filter(warehouse_id=warehouse_id)

    options = '<option value="">Select Location</option>'  
    for location in locations:
        options += f'<option value="{location.id}">{location.name}</option>'
    return JsonResponse(options, safe=False)




@login_required
def complete_quality_control(request, qc_id):
    quality_control = get_object_or_404(QualityControl, id=qc_id)
    
    good_quantity = quality_control.good_quantity

    purchase_dispatch_item = quality_control.purchase_dispatch_item
    purchase_shipment = purchase_dispatch_item.purchase_shipment
    purchase_order = purchase_shipment.purchase_order
    purchase_request_order = purchase_order.purchase_request_order

    if request.method == 'POST':
        selected_warehouse_id = request.POST.get('warehouse')
        selected_warehouse = Warehouse.objects.get(id=selected_warehouse_id) if selected_warehouse_id else None

        form = QualityControlCompletionForm(request.POST, warehouse=selected_warehouse)
        if form.is_valid():
            warehouse = form.cleaned_data['warehouse']
            location = form.cleaned_data['location']

            inventory_transaction = InventoryTransaction.objects.create(
                user=request.user,
                warehouse=warehouse,
                location=location,
                product=quality_control.product,
                transaction_type='INBOUND',
                quantity=good_quantity,
                purchase_order=purchase_dispatch_item.dispatch_item.purchase_order
            )

            inventory, created = Inventory.objects.get_or_create(
                warehouse=warehouse,
                location=location,
                product=quality_control.product,
                defaults={
                    'quantity': good_quantity 
                }
            )
   
            if not created:
                inventory.quantity += good_quantity
                inventory.save()
                messages.success(request, "Inventory updated successfully.")
            else:
                messages.success(request, "Inventory created successfully.")
        

         
            purchase_dispatch_item.status = 'DELIVERED'
            purchase_dispatch_item.save()   

            update_purchase_order(purchase_order.id)
            update_shipment_status(purchase_shipment.id)
            update_purchase_request_order(purchase_request_order.id)  
       


            messages.success(request, "Quality control completed and product added to inventory.")
            return redirect('purchase:qc_dashboard')
        else:          
            messages.error(request, "Failed to update inventory. Form is not valid.")
    else:
        form = QualityControlCompletionForm()

    return render(request, 'inventory/complete_quality_control.html', {
        'form': form,
        'quality_control': quality_control,
    })



# @login_required
# def complete_sale_quality_control(request, qc_id):
#     quality_control = get_object_or_404(SaleQualityControl, id=qc_id)

#     total_quantity = quality_control.total_quantity
#     good_quantity = quality_control.good_quantity
#     bad_quantity = quality_control.bad_quantity

#     sale_order_item = quality_control.sale_dispatch_item
#     sale_dispatch_item = quality_control.sale_dispatch_item
#     sale_shipment =  sale_dispatch_item.sale_shipment
#     sale_order = sale_shipment.sale_order
#     sale_request_order = sale_order.sale_request

#     if request.method == 'POST':
#         selected_warehouse_id = request.POST.get('warehouse')
#         selected_warehouse = Warehouse.objects.get(id=selected_warehouse_id) if selected_warehouse_id else None

#         form = QualityControlCompletionForm(request.POST, warehouse=selected_warehouse)
#         if form.is_valid():
#             warehouse = form.cleaned_data['warehouse']
#             location = form.cleaned_data['location']
           
#             inventory_transaction = InventoryTransaction.objects.create(
#                 user=request.user,
#                 warehouse=warehouse,
#                 location=location,
#                 product=quality_control.product,
#                 transaction_type='OUTBOUND', 
#                 quantity=good_quantity,
#                 sales_order=sale_order_item.dispatch_item.sale_order
#             )
#             if not inventory_transaction.update_inventory():
#                 raise ValueError(f"Failed to update stock for {quality_control.product.name} in {warehouse.name}")


#             update_sale_order(sale_order.id)
#             update_sale_shipment_status(sale_shipment.id)
#             update_sale_request_order(sale_request_order.id)

#             messages.success(request, "Quality control completed and product deducted from warehouse.")
#             return redirect('sales:qc_dashboard')
#         else:
#             print("Form errors:", form.errors)
#     else:
#         form = QualityControlCompletionForm()

#     return render(request, 'inventory/complete_quality_control.html', {
#         'form': form,
#         'quality_control': quality_control,
#     })


import uuid
from manufacture.models import MaterialsRequestOrder

@login_required
def complete_manufacture_quality_control(request, qc_id):

    quality_control = get_object_or_404(ManufactureQualityControl, id=qc_id)

    total_quantity = quality_control.total_quantity
    good_quantity = quality_control.good_quantity
    bad_quantity = quality_control.bad_quantity

    if good_quantity + bad_quantity > total_quantity:
        messages.error(request, "Invalid quantities: good + bad exceeds total.")
        return redirect('manufacture:qc_dashboard')

    materials_request_order = quality_control.finish_goods_from_production.materials_request_order
    if not materials_request_order:
       materials_request_order = MaterialsRequestOrder.objects.create(
        order_id=f"DFGS-{uuid.uuid4().hex[:8].upper()}"
    )
   
    finish_goods_from_production = quality_control.finish_goods_from_production
    finish_goods_from_production.materials_request_order = materials_request_order
    finish_goods_from_production.save()

    if request.method == 'POST':
        selected_warehouse_id = request.POST.get('warehouse')
        selected_warehouse = get_object_or_404(Warehouse, id=selected_warehouse_id) if selected_warehouse_id else None

        form = QualityControlCompletionForm(request.POST, warehouse=selected_warehouse)
        if form.is_valid():
            warehouse = form.cleaned_data['warehouse']
            location = form.cleaned_data['location']

            if InventoryTransaction.objects.filter(
                manufacture_order=materials_request_order,
                transaction_type='MANUFACTURE_IN',
                product=quality_control.product,
            ).exists():
                messages.error(request, "This transaction has already been recorded.")
                return redirect('manufacture:qc_dashboard')

            inventory_transaction = InventoryTransaction.objects.create(
                user=request.user,
                warehouse=warehouse,
                location=location,
                product=quality_control.product,
                transaction_type='MANUFACTURE_IN',
                quantity=good_quantity,
                manufacture_order=materials_request_order,
            )
            inventory, created = Inventory.objects.get_or_create(
                warehouse=warehouse,
                location=location,
                product=quality_control.product,
                defaults={
                    'quantity': good_quantity 
                }
            )
   
            if not created:
                inventory.quantity += good_quantity
                inventory.save()
                messages.success(request, "Inventory updated successfully.")
            else:
                messages.success(request, "Inventory created successfully.")
         
            quality_control.finish_goods_from_production.status = 'RECEIVED'
            quality_control.finish_goods_from_production.save()

            messages.success(request, "Quality control completed and product added to inventory.")
            return redirect('manufacture:qc_dashboard')
        else:
            print("Form errors:", form.errors)
    else:
        form = QualityControlCompletionForm()

    return render(request, 'inventory/complete_quality_control.html', {
        'form': form,
        'quality_control': quality_control,
    })



####################  Transfer section ##############################################

def create_transfer(request):
    if 'transfer_basket' not in request.session:
        request.session['transfer_basket'] = []

    form = TransferProductForm(request.POST or None)
    if request.method == 'POST':
        if 'add_to_basket' in request.POST:
            if form.is_valid():
                product = form.cleaned_data['product']
                source_warehouse = form.cleaned_data['source_warehouse']
                target_warehouse = form.cleaned_data['target_warehouse']
                quantity = form.cleaned_data['quantity']

                transfer_basket = request.session.get('transfer_basket', [])
                product_in_basket = next((item for item in transfer_basket if item['id'] == product.id and item['source_warehouse_id'] == source_warehouse.id and item['target_warehouse_id'] == target_warehouse.id), None)

                if product_in_basket:
                    product_in_basket['quantity'] += quantity
                else:
                    transfer_basket.append({
                        'id': product.id,
                        'product_name': product.name,
                        'sku': product.sku,
                        'quantity': quantity,
                        'source_warehouse_id': source_warehouse.id,
                        'source_warehouse_name': source_warehouse.name,
                        'target_warehouse_id': target_warehouse.id,
                        'target_warehouse_name': target_warehouse.name,
                    })

                request.session['transfer_basket'] = transfer_basket
                request.session.modified = True
                messages.success(request, f"Added '{product.name}' to the transfer basket")
                return redirect('inventory:create_transfer')
            else:
                messages.error(request, "Form is invalid. Please check the details and try again.")

        elif 'action' in request.POST:
            action = request.POST.get('action')
            product_id = int(request.POST.get('product_id', 0))
            source_warehouse_id = int(request.POST.get('source_warehouse_id', 0))
            target_warehouse_id = int(request.POST.get('target_warehouse_id', 0))

            if action == 'update':
                new_quantity = int(request.POST.get('quantity', 1))
                for item in request.session['transfer_basket']:
                    if item['id'] == product_id and item['source_warehouse_id'] == source_warehouse_id and item['target_warehouse_id'] == target_warehouse_id:
                        item['quantity'] = new_quantity
                        break
                messages.success(request, "Quantity updated successfully.")

            elif action == 'delete':
                request.session['transfer_basket'] = [
                    item for item in request.session['transfer_basket']
                    if not (item['id'] == product_id and item['source_warehouse_id'] == source_warehouse_id and item['target_warehouse_id'] == target_warehouse_id)
                ]
                messages.success(request, "Product removed successfully.")
                
            request.session.modified = True
            return redirect('inventory:create_transfer')

        elif 'confirm_transfer' in request.POST:
            transfer_basket = request.session.get('transfer_basket', [])
            if not transfer_basket:
                messages.error(request, "Transfer basket is empty. Add products before confirming the transfer.")
                return redirect('inventory:create_transfer')
            return redirect('inventory:confirm_transfer')
    transfer_basket = request.session.get('transfer_basket', [])
    return render(request, 'inventory/transfer/create_transfer.html', {'form': form, 'transfer_basket': transfer_basket})




def confirm_transfer(request):
    transfer_basket = request.session.get('transfer_basket', [])
    if not transfer_basket:
        messages.error(request, "Transfer basket is empty. Cannot confirm the transfer.")
        return redirect('inventory:create_transfer')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                transfer_order = TransferOrder.objects.create(
                    order_number='TO-' + str(int(now().timestamp())),
                )

                for item in transfer_basket:
                    product = get_object_or_404(Product, id=item['id'])
                    source_warehouse = get_object_or_404(Warehouse, id=item['source_warehouse_id'])
                    target_warehouse = get_object_or_404(Warehouse, id=item['target_warehouse_id'])
                    transfer_quantity = item['quantity']

                    source_stock = get_warehouse_stock(source_warehouse, product)
                    if source_stock < transfer_quantity:
                        messages.error(
                            request,
                            f"Not enough stock for {product.name} in {source_warehouse.name}. "
                            f"Available: {source_stock}, Requested: {transfer_quantity}"
                        )
                        return redirect('inventory:create_transfer')

                    transaction_out = InventoryTransaction.objects.create(
                        user=request.user,
                        warehouse=source_warehouse,
                        product=product,
                        transaction_type='TRANSFER_OUT',
                        quantity=transfer_quantity,
                        transaction_date=now(),
                        remarks=f"Transferred {transfer_quantity} units of {product.name} to {target_warehouse.name}"
                    )
                    source_inventory, created = Inventory.objects.get_or_create(
                    warehouse=source_warehouse,
                    product=product,                    
                    defaults={'quantity': 0} )

                    if not created:
                        if source_inventory.quantity >= transfer_quantity:
                            source_inventory.quantity -= transfer_quantity
                            source_inventory.save()  
                        else:
                            raise ValueError(f"Insufficient quantity in {source_warehouse.name} for {product.name}")
                    else:
                       
                        source_inventory.quantity -= transfer_quantity
                        source_inventory.save()


                    transaction_in = InventoryTransaction.objects.create(
                        user=request.user,
                        warehouse=target_warehouse,
                        product=product,
                        transaction_type='TRANSFER_IN',
                        quantity=transfer_quantity,
                        transaction_date=now(),
                        remarks=f"Received {transfer_quantity} units of {product.name} from {source_warehouse.name}"
                    )
                    target_inventory, created = Inventory.objects.get_or_create(
                    warehouse=target_warehouse,
                    product=product,                  
                    defaults={'quantity': 0} )

                    if not created:
                        target_inventory.quantity += transfer_quantity  
                                           
                    else:
                        target_inventory.quantity = transfer_quantity
                    target_inventory.save()
                   

                    TransferItem.objects.create(
                        product=product,
                        transfer_order=transfer_order,
                        source_warehouse=source_warehouse,
                        target_warehouse=target_warehouse,
                        quantity=transfer_quantity,
                        remarks=f"Transferred {transfer_quantity} units of {product.name}"
                    )

                transfer_order.order_status = 'COMPLETED'
                transfer_order.save()

                request.session['transfer_basket'] = []
                request.session.modified = True
                messages.success(request, "Transfer order processed successfully!")
                return redirect('inventory:create_transfer')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('inventory:create_transfer')

    return render(request, 'inventory/transfer/confirm_transfer.html', {'transfer_basket': transfer_basket})



def transfer_order_list(request):
    transfer_order=None
    
    transfer_orders = TransferOrder.objects.all().order_by('-created_at') 
    form = CommonFilterForm(request.GET or None)
    if form.is_valid():
        transfer_order = form.cleaned_data['transfer_id']
        if transfer_order:
            transfer_orders = transfer_orders.filter(order_number = transfer_order)

    paginator = Paginator(transfer_orders,10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form=CommonFilterForm()

    return render(request, 'inventory/transfer/transfer_order_list.html', {
        'transfer_orders': transfer_orders,  
        'page_obj':page_obj,
        'form':form,
        'transfer_order':transfer_order
        
    })


def transfer_order_detail(request,transfer_order_id):
    transfer_order = get_object_or_404(TransferOrder, id=transfer_order_id)
    transferred_products =TransferItem.objects.filter(transfer_order=transfer_order)
    return render(request, 'inventory/transfer/transfer_order_details.html', {
       
        'transferred_products': transferred_products,
    })


def all_inventory(request):
    return redirect(request,'inventory/all_inventory.html')

def inventory_list(request):   
    products = Product.objects.all()
    warehouses = Warehouse.objects.all()
    data = []
    grand_total_stock_value = 0
    days = None
    start_date = None
    end_date = None
    date_filter = {}
    warehouse_name=None
    product_name=None
    grouped_data = []
    chart_data={}
  
  

    form = SummaryReportChartForm(request.GET or None)

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        warehouse_name = form.cleaned_data.get('warehouse_name')
        product_name = form.cleaned_data.get('product_name')

        if product_name:
            products = products.filter(id=product_name.id)
        if warehouse_name:
            warehouses = warehouses.filter(id=warehouse_name.id)

        if start_date and end_date:
            date_filter = {'created_at__range': (start_date, end_date)}
        elif days:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            date_filter = {'created_at__range': (start_date, end_date)}
        else:
            date_filter = {}

        for product in products:
            inventories = product.product_inventories.filter(**date_filter)  
            if warehouse_name:
                inventories = inventories.filter(warehouse=warehouse_name)  

            for inventory in inventories:
                stock_data = calculate_stock_value(product, inventory.warehouse)

                total_available = stock_data['total_available']
                total_stock_value = total_available * float(product.unit_price)

                grand_total_stock_value += total_stock_value
                

                data.append({
                    'product': product.name,
                    'warehouse': inventory.warehouse,

                    'total_stock': stock_data['total_stock'],
                    'total_purchase': stock_data['total_purchase'],
                    'total_sold': stock_data['total_sold'],

                    'total_manufacture_in': stock_data['total_manufacture_in'],
                    'total_manufacture_out': stock_data['total_manufacture_out'],

                    'total_existing_in': stock_data['total_existing_in'],
                    'total_operations_out': stock_data['total_operations_out'],
                    'total_transfer_out': stock_data['total_transfer_out'],
                    'total_transfer_in': stock_data['total_transfer_in'],
               
                    'total_replacement_out': stock_data['total_replacement_out'],
                    'total_replacement_in': stock_data['total_replacement_in'], 
                    'total_scrapped_out': stock_data['total_scrapped_out'],
                    'total_scrapped_in': stock_data['total_scrapped_in'],                     
              
                    'total_available': total_available,            
                    'total_stock_value': total_stock_value,
                })

        chart_data = {
            'labels': [f"{item['product']} ({item['warehouse'].name})" for item in data],

            'total_stock': [item['total_stock'] for item in data],
            'total_purchase': [item['total_purchase'] for item in data],  
            'total_sold': stock_data['total_sold'],
            'total_manufacture_in': [item['total_manufacture_in'] for item in data],
            'total_manufacture_out': [item['total_manufacture_out'] for item in data],

            'total_existing_in': [item['total_existing_in'] for item in data],
            'total_operations_out': [item['total_operations_out'] for item in data],
            'total_transfer_in': [item['total_transfer_in'] for item in data],
            'total_transfer_out': [item['total_transfer_out'] for item in data],

            'total_replacement_out': [item['total_replacement_out'] for item in data],
            'total_replacement_in': [item['total_replacement_in'] for item in data],
            'total_scrapped_out': [item['total_scrapped_out'] for item in data],
            'total_scrapped_in': [item['total_scrapped_in'] for item in data],
            'total_available': [item['total_available'] for item in data],  
            'total_stock_value': [item['total_stock_value'] for item in data],
        }

    warehouse_json = json.dumps(chart_data)
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    grouped_data = []
    for warehouse, items in groupby(sorted(data, key=lambda x: x['warehouse'].name), key=lambda x: x['warehouse'].name):
        items_list = list(items)
        warehouse_total_stock_value = sum(item['total_stock_value'] for item in items_list)
        grouped_data.append((warehouse, items_list, warehouse_total_stock_value))

    form=SummaryReportChartForm()
    context = {
        'grouped_data': grouped_data,
        'product_wise_data': page_obj,
        'warehouse_json': warehouse_json,
        'grand_total_stock_value': grand_total_stock_value,
        'form': form,
        'days': days,
        'start_date': start_date,
        'end_date': end_date,
        'warehouse_name':warehouse_name,
        'product_name':product_name
    }
    return render(request, 'inventory/inventory_list.html', context)



def inventory_aggregate_list(request):   
    aggregated_data = []
    grand_total_stock_value = 0
    days = None
    start_date = None
    end_date = None
    warehouse_name=None
    product_name=None
    products = None

    form = SummaryReportChartForm(request.GET or None)

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        product_name = form.cleaned_data.get('product_name')
        warehouse_name = form.cleaned_data.get('warehouse_name')

        products = Product.objects.all().distinct()
        if products:
            if product_name:
                products = products.filter(id=product_name.id)

            if start_date and end_date:
                products = products.filter(
                    product_inventories__created_at__range=(start_date, end_date)
                ).distinct()
            elif days:
                end_date = timezone.now()
                start_date = end_date - timedelta(days=days)
                products = products.filter(
                    product_inventories__created_at__range=(start_date, end_date)
                ).distinct()

            for product in products:
                inventories = product.product_inventories.all()  
                if start_date and end_date:
                    inventories = inventories.filter(created_at__range=(start_date, end_date))
                elif days:
                    inventories = inventories.filter(created_at__range=(start_date, end_date))

        stock_data = calculate_stock_value2(product)
        total_available = stock_data['total_available']
        total_stock_value = total_available * float(product.unit_price)

        grand_total_stock_value += total_stock_value
        product_name = product



        aggregated_data.append({
            'product': product.name,

            'total_stock': stock_data['total_stock'],
            'total_purchase': stock_data['total_purchase'],
            'total_sold': stock_data['total_sold'],
            'total_available': total_available,

            'total_manufacture_in': stock_data['total_manufacture_in'],
            'total_manufacture_out': stock_data['total_manufacture_out'],
            'total_existing_in': stock_data['total_existing_in'],
            'total_operations_out': stock_data['total_operations_out'],

            'total_transfer_in': stock_data['total_transfer_in'],  
            'total_transfer_out': stock_data['total_transfer_out'],    
            
            'total_scrapped_in': stock_data['total_scrapped_in'],  
            'total_scrapped_out': stock_data['total_scrapped_out'],      
            'total_replacement_out': stock_data['total_replacement_out'],
            'total_replacement_in': stock_data['total_replacement_in'],        
                             
            'total_stock_value': total_stock_value,
        })

    chart_data = {
        'labels': [f"{item['product']}" for item in aggregated_data],

        'total_stock': [item['total_stock'] for item in aggregated_data],
        'total_purchase': [item['total_purchase'] for item in aggregated_data],
        'total_sold': [item['total_sold'] for item in aggregated_data],
        'total_available': [item['total_available'] for item in aggregated_data],

        'total_manufacture_in': [item['total_manufacture_in'] for item in aggregated_data],
        'total_manufacture_out': [item['total_manufacture_out'] for item in aggregated_data],
        'total_existing_in': [item['total_existing_in'] for item in aggregated_data],
        'total_operations_out': [item['total_operations_out'] for item in aggregated_data],

        'total_transfer_in': [item['total_transfer_in'] for item in aggregated_data],  
        'total_transfer_out': [item['total_transfer_out'] for item in aggregated_data],  
        'total_scrapped_in': [item['total_scrapped_in'] for item in aggregated_data],  
        'total_scrapped_out': [item['total_scrapped_out'] for item in aggregated_data],    
        'total_replacement_out': [item['total_replacement_out'] for item in aggregated_data],
        'total_replacement_in': [item['total_replacement_in'] for item in aggregated_data],      
       
        'total_stock_value': [item['total_stock_value'] for item in aggregated_data],
       
    }

    warehouse_json = json.dumps(chart_data)

    paginator = Paginator(aggregated_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form=SummaryReportChartForm()
    context = {
        'page_obj': page_obj,
        'warehouse_json': warehouse_json,
        'grand_total_stock_value': grand_total_stock_value,
        'form': form,
        'days': days,
        'start_date': start_date,
        'end_date': end_date,
        'warehouse_name':warehouse_name,
        'product_name':product_name,
        'reported_product':product_name
    }
    return render(request, 'inventory/inventory_aggregate_list.html', context)




def inventory_executive_sum(request):
    products = Product.objects.all()
 
    warehouse_data = {}
    grand_total_stock_value = 0
    chart_data = []  

    for product in products:
        inventories = product.product_inventories.all()
        for inventory in inventories:
            stock = calculate_stock_value(product, inventory.warehouse)
            stock_value = float(stock['total_available'] * product.unit_price)
            grand_total_stock_value += stock_value

            if inventory.warehouse.name not in warehouse_data:
                warehouse_data[inventory.warehouse.name] = 0
            warehouse_data[inventory.warehouse.name] += stock_value

    for warehouse, stock_value in warehouse_data.items():
        chart_data.append({
            'warehouse': warehouse,
            'stock_value': float(stock_value), 
        })

    chart_data_json = json.dumps(chart_data)

    context = {
        'chart_data': chart_data,
        'chart_data_json': chart_data_json,
        'grand_total_stock_value': grand_total_stock_value,
    }
    return render(request, 'inventory/inventory_executive_sum.html', context)


