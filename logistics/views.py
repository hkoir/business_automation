
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from.models import  PurchaseShipment,SaleShipment,PurchaseDispatchItem
from django.contrib import messages
from django.db import transaction
import uuid
from django.db.models import Sum
from django.db import IntegrityError
from collections import defaultdict
import logging
logger = logging.getLogger(__name__)

from .forms import PurchaseShipmentForm,PurchaseDispatchItemForm,SaleDispatchItemForm,SaleShipmentForm
from .models import  PurchaseDispatchItem, PurchaseOrderItem,SaleDispatchItem,Warehouse,Location
from sales.models import SaleOrderItem,SaleQualityControl,SaleOrder
from purchase.models import  QualityControl,PurchaseOrder




@login_required
def create_purchase_shipment(request, purchase_order_id):
    purchase_order = get_object_or_404(PurchaseOrder, id=purchase_order_id)
    permission_status = purchase_order.approver_approval_status
    if not permission_status:
        messages.error(request,'You can not proceed due to pending permission')
        return redirect('purchase:purchase_order_list')

    if request.method == 'POST':
        form = PurchaseShipmentForm(request.POST)
        if form.is_valid():
            shipment = form.save(commit=False)
            shipment.user = request.user
            shipment.purchase_order = purchase_order
            shipment.save()
            return redirect('logistics:purchase_shipment_detail', shipment_id=shipment.id)
    else:
        form = PurchaseShipmentForm()

    return render(request, 'logistics/purchase/create_shipment.html', {
        'form': form,
        'purchase_order': purchase_order,
    })



def purchase_shipment_list(request):
    purchase_shipments = PurchaseShipment.objects.all()
    return render(request,'logistics/purchase/shipment_list.html',{'purchase_shipments':purchase_shipments})




@login_required
def purchase_shipment_detail(request, shipment_id):
    shipment = get_object_or_404(PurchaseShipment, id=shipment_id)
    tracking_updates = shipment.purchase_shipment_tracking.all()

    return render(request, 'logistics/purchase/shipment_details.html', {
        'shipment': shipment,
        'tracking_updates': tracking_updates,
    })




def create_purchase_dispatch_item(request, dispatch_id):
    purchase_shipment = get_object_or_404(PurchaseShipment, id=dispatch_id)
    if 'basket' not in request.session:
        request.session['basket'] = []
    form = PurchaseDispatchItemForm(request.POST,purchase_shipment=purchase_shipment)    
    if request.method == 'POST':
        if 'add_to_basket' in request.POST:
            if form.is_valid():

                purchase_shipment = form.cleaned_data['purchase_shipment']
                dispatch_item = form.cleaned_data['dispatch_item']
                dispatch_quantity = form.cleaned_data['dispatch_quantity']
                dispatch_date = form.cleaned_data['dispatch_date']
                delivery_date = form.cleaned_data['delivery_date']

                dispatched_quantity_total = (
                    dispatch_item.order_dispatch_item.aggregate(total=Sum('dispatch_quantity'))['total'] or 0
                )

                total_in_basket = sum(
                    item['quantity'] for item in request.session['basket'] if item['id'] == dispatch_item.id
                )
                
                if dispatched_quantity_total + total_in_basket + dispatch_quantity > dispatch_item.quantity:
                    messages.error(request, f"Cannot add {dispatch_quantity} units of '{dispatch_item.product.name}' to the dispatch. The total dispatch quantity would exceed the ordered quantity.")
                    return redirect('logistics:create_purchase_dispatch_item', dispatch_id=dispatch_id)

                dispatch_date_str = dispatch_date.strftime('%Y-%m-%d') if dispatch_date else None
                delivery_date_str = delivery_date.strftime('%Y-%m-%d') if delivery_date else None

                basket = request.session.get('basket', [])
                product_in_basket = next(
                    (item for item in basket if item['id'] == dispatch_item.id), 
                    None
                )

                if product_in_basket:
                    product_in_basket['dispatch_quantity'] += dispatch_quantity
                else:
                    basket.append({
                        'id': dispatch_item.id,
                        'name': dispatch_item.product.name,
                        'quantity': dispatch_quantity,
                        'dispatch_date': dispatch_date_str,
                        'delivery_date': delivery_date_str,
                        'purchase_shipment_id': purchase_shipment.id
                    })

                request.session['basket'] = basket
                request.session.modified = True
                messages.success(request, f"Added '{dispatch_item.product.name}' to the purchase basket")
                return redirect('logistics:create_purchase_dispatch_item', dispatch_id=dispatch_id)

            else:
                messages.error(request, "Form is invalid. Please check the details and try again.")
        
        elif 'action' in request.POST:
            action = request.POST['action']
            product_id = int(request.POST.get('product_id', 0))

            if action == 'update':
                new_quantity = int(request.POST.get('quantity', 1))
                for item in request.session['basket']:
                    if item['id'] == product_id:
                        item['quantity'] = new_quantity
                        break
            elif action == 'delete':
                request.session['basket'] = [
                    item for item in request.session['basket'] if item['id'] != product_id
                ]

            request.session.modified = True
            messages.success(request, "Basket updated successfully.")
            return redirect('logistics:create_purchase_dispatch_item', dispatch_id=purchase_shipment.id)

        elif 'confirm_dispatch' in request.POST:
            basket = request.session.get('basket', [])
            if not basket:
                messages.error(request, "The dispatch basket is empty. Add items before confirming.")
                return redirect('logistics:create_purchase_dispatch_item', dispatch_id=purchase_shipment.id)

            return redirect('logistics:confirm_purchase_dispatch_item')

    basket = request.session.get('basket', [])
    form = PurchaseDispatchItemForm(purchase_shipment=purchase_shipment)  
    return render(request, 'logistics/purchase/create_purchase_dispatch_item.html', {
        'form': form,
        'basket': basket,
        'purchase_shipment': purchase_shipment,
    })




def confirm_purchase_dispatch_item(request):
    basket = request.session.get('basket', [])

    purchase_shipment_id = basket[0].get('purchase_shipment_id') if basket else None
    if not basket or not purchase_shipment_id:
        messages.error(request, "The dispatch basket is empty or Purchase shipment ID is missing. Please add items to the dispatch basket.")       
        return redirect('logistics:dispatch_item_list') 
    purchase_shipment = get_object_or_404(PurchaseShipment, id=purchase_shipment_id)

    if request.method == 'POST':
        try:
            with transaction.atomic():

                for item in basket:
                    dispatch_item = get_object_or_404(PurchaseOrderItem, id=item['id'])

                    PurchaseDispatchItem.objects.create(
                        purchase_shipment=purchase_shipment,
                        dispatch_item=dispatch_item,
                        dispatch_quantity=item['quantity'],
                        dispatch_date=item['dispatch_date'],
                        delivery_date=item['delivery_date'],
                        status='IN_PROCESS',
                        user=request.user,
                    )

                request.session['basket'] = []
                request.session.modified = True

                messages.success(request, "Purchase dispatch confirmed and created successfully.")
                return redirect('logistics:create_purchase_dispatch_item', dispatch_id=purchase_shipment.id)

        except Exception as e:
            messages.error(request, f"An error occurred while confirming the dispatch: {str(e)}")
            return redirect('logistics:create_purchase_dispatch_item', dispatch_id=purchase_shipment.id)

    return render(request, 'logistics/purchase/confirm_purchase_dispatch_item.html', {'basket': basket})





@login_required
def dispatch_item_list(request, purchase_order_id):
    purchase_order = get_object_or_404(PurchaseOrder, id=purchase_order_id)
    dispatch_items = PurchaseDispatchItem.objects.filter(dispatch_item__purchase_order=purchase_order)

    product_wise_totals = defaultdict(lambda: {
        'order_quantity': 0,
        'dispatch_quantity': 0,
        'good_quantity': 0,
        'bad_quantity': 0
    })

    shipments = {}
    qc_quantities = {} 

    for dispatch_item in dispatch_items:
        shipment = dispatch_item.purchase_shipment
        product_name = dispatch_item.dispatch_item.product.name
        if shipment not in shipments:
            shipments[shipment] = []
        shipments[shipment].append(dispatch_item)

        product_wise_totals[product_name]['order_quantity'] += dispatch_item.dispatch_item.quantity or 0
        product_wise_totals[product_name]['dispatch_quantity'] += dispatch_item.dispatch_quantity or 0

        qc_entry = QualityControl.objects.filter(purchase_dispatch_item=dispatch_item).first()
        if qc_entry:
            good_quantity = qc_entry.good_quantity or 0
            bad_quantity = qc_entry.bad_quantity or 0

            product_wise_totals[product_name]['good_quantity'] += good_quantity
            product_wise_totals[product_name]['bad_quantity'] += bad_quantity

            qc_quantities[dispatch_item.id] = {
                'good_quantity': good_quantity,
                'bad_quantity': bad_quantity,
                'created_at': qc_entry.created_at
            }
        else:
            product_wise_totals[product_name]['good_quantity'] += 0
            product_wise_totals[product_name]['bad_quantity'] += 0

    context = {
        'purchase_order': purchase_order,
        'shipments': shipments,
        'product_wise_totals': dict(product_wise_totals),
        'qc_quantities': qc_quantities,    }

    return render(request, 'logistics/purchase/dispatch_item_list.html', context)


def update_dispatch_status(request, dispatch_item_id):
    dispatch_item = get_object_or_404(PurchaseDispatchItem, id=dispatch_item_id)
    if request.method == 'POST':
        new_status = request.POST.get('new_status')
        dispatch_item.status = new_status
        dispatch_item.save()        

    shipment = dispatch_item.purchase_shipment
    shipment.update_shipment_status()

    try:
        shipment = PurchaseShipment.objects.get(id=shipment.id)
        all_items_delivered = shipment.shipment_dispatch_item.filter(status='REACHED').count() == shipment.shipment_dispatch_item.count()
        if all_items_delivered:
            shipment.status = 'REACHED'
            shipment.save()
            logger.info(f"Shipment {shipment.id} marked as DELIVERED.")
    except PurchaseShipment.DoesNotExist:
        logger.error(f"Shipment {shipment.id} not found.")

    return redirect('logistics:dispatch_item_list', purchase_order_id=shipment.purchase_order.id)



def cancel_dispatch_item(request, dispatch_item_id):
    dispatch_item = get_object_or_404(PurchaseDispatchItem, id=dispatch_item_id)

    if request.method == "POST":
        dispatch_item.status = 'CANCELLED'
        dispatch_item.save()
        messages.success(request, "Dispatch item successfully cancelled.")

        return redirect('logistics:dispatch_item_list', purchase_order_id=dispatch_item.dispatch_item.purchase_order.id)
    return render(request, 'logistics/purchase/cancel_order_item.html', {'dispatch_item': dispatch_item})







############################ sale shipmen t###########################################################################

@login_required
def create_sale_shipment(request, sale_order_id):
    sale_order = get_object_or_404(SaleOrder, id=sale_order_id)

    if request.method == 'POST':
        form = SaleShipmentForm(request.POST, sale_order=sale_order)
        if form.is_valid():
            shipment = form.save(commit=False)
            shipment.user = request.user
            shipment.sale_order = sale_order
            shipment.save()
            return redirect('logistics:sale_shipment_detail', shipment_id=shipment.id)
    else:
        form = SaleShipmentForm(sale_order=sale_order)

    return render(request, 'logistics/sales/create_shipment.html', {
        'form': form,
        'sale_order': sale_order,
    })



def sale_shipment_list(request):
    sale_shipments = SaleShipment.objects.all()
    return render(request,'logistics/sales/shipment_list.html',{'sale_shipments':sale_shipments})




@login_required
def sale_shipment_detail(request, shipment_id):
    shipment = get_object_or_404(SaleShipment, id=shipment_id)
    tracking_updates = shipment.sale_shipment_tracking.all()

    return render(request, 'logistics/sales/shipment_details.html', {
        'shipment': shipment,
        'tracking_updates': tracking_updates,
    })



def create_sale_dispatch_item(request, dispatch_id):
    sale_shipment = get_object_or_404(SaleShipment, id=dispatch_id)
    if 'basket' not in request.session:
        request.session['basket'] = []
    form = SaleDispatchItemForm(request.POST,sale_shipment=sale_shipment)    
    if request.method == 'POST':
        if 'add_to_basket' in request.POST:
            if form.is_valid():

                sale_shipment = form.cleaned_data['sale_shipment']
                dispatch_item = form.cleaned_data['dispatch_item']
                dispatch_quantity = form.cleaned_data['dispatch_quantity']
                dispatch_date = form.cleaned_data['dispatch_date']
                delivery_date = form.cleaned_data['delivery_date']
                warehouse = form.cleaned_data['warehouse']
                location = form.cleaned_data['location']

                dispatched_quantity_total = (
                    dispatch_item.sale_dispatch_item.aggregate(total=Sum('dispatch_quantity'))['total'] or 0
                )

                total_in_basket = sum(
                    item['quantity'] for item in request.session['basket'] if item['id'] == dispatch_item.id
                )
                
                if dispatched_quantity_total + total_in_basket + dispatch_quantity > dispatch_item.quantity:
                    messages.error(request, f"Cannot add {dispatch_quantity} units of '{dispatch_item.product.name}' to the dispatch. The total dispatch quantity would exceed the ordered quantity.")
                    return redirect('logistics:create_purchase_dispatch_item', dispatch_id=dispatch_id)

                dispatch_date_str = dispatch_date.strftime('%Y-%m-%d') if dispatch_date else None
                delivery_date_str = delivery_date.strftime('%Y-%m-%d') if delivery_date else None

                basket = request.session.get('basket', [])
                product_in_basket = next(
                    (item for item in basket if item['id'] == dispatch_item.id), 
                    None
                )

                if product_in_basket:
                    product_in_basket['dispatch_quantity'] += dispatch_quantity
                else:
                    basket.append({
                        'id': dispatch_item.id,
                        'name': dispatch_item.product.name,
                        'quantity': dispatch_quantity,
                        'dispatch_date': dispatch_date_str,
                        'delivery_date': delivery_date_str,
                        'sale_shipment_id': sale_shipment.id,
                        'warehouse': warehouse.id,
                        'location': location.id
                    })

                request.session['basket'] = basket
                request.session.modified = True
                messages.success(request, f"Added '{dispatch_item.product.name}' to the purchase basket")
                return redirect('logistics:create_sale_dispatch_item', dispatch_id=dispatch_id)

            else:
                messages.error(request, "Form is invalid. Please check the details and try again.")
        
        elif 'action' in request.POST:
            action = request.POST['action']
            product_id = int(request.POST.get('product_id', 0))

            if action == 'update':
                new_quantity = int(request.POST.get('quantity', 1))
                for item in request.session['basket']:
                    if item['id'] == product_id:
                        item['quantity'] = new_quantity
                        break
            elif action == 'delete':
                request.session['basket'] = [
                    item for item in request.session['basket'] if item['id'] != product_id
                ]

            request.session.modified = True
            messages.success(request, "Basket updated successfully.")
            return redirect('logistics:create_sale_dispatch_item', dispatch_id=sale_shipment.id)

        elif 'confirm_dispatch' in request.POST:
            basket = request.session.get('basket', [])
            if not basket:
                messages.error(request, "The dispatch basket is empty. Add items before confirming.")
                return redirect('logistics:sale_dispatch_item', dispatch_id=sale_shipment.id)

            return redirect('logistics:confirm_sale_dispatch_item')
    form = SaleDispatchItemForm(sale_shipment=sale_shipment)  
    basket = request.session.get('basket', [])
    return render(request, 'logistics/sales/create_sale_dispatch_item.html', {
        'form': form,
        'basket': basket,
        'sale_shipment': sale_shipment,
    })




def confirm_sale_dispatch_item(request):
    basket = request.session.get('basket', [])

    sale_shipment_id = basket[0].get('sale_shipment_id') if basket else None
    warehouse_id = basket[0].get('warehouse') if basket else None
    location_id = basket[0].get('location') if basket else None
    
    if not basket or not sale_shipment_id:
        messages.error(request, "The dispatch basket is empty or Purchase shipment ID is missing. Please add items to the dispatch basket.")       
        return redirect('logistics:create_sale_dispatch_item', dispatch_id=sale_shipment_id.id)

    sale_shipment_id = get_object_or_404(SaleShipment, id=sale_shipment_id)
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)
    location = get_object_or_404(Location, id=location_id)

    if request.method == 'POST':
        try:
            with transaction.atomic():

                for item in basket:
                    dispatch_item = get_object_or_404(SaleOrderItem, id=item['id'])

                    SaleDispatchItem.objects.create(
                        sale_shipment=sale_shipment_id,
                        dispatch_item=dispatch_item,
                        dispatch_quantity=item['quantity'],
                        dispatch_date=item['dispatch_date'],
                        delivery_date=item['delivery_date'],
                        warehouse = warehouse,
                        location=location,
                        status='DISPATCHED',
                        user=request.user,
                    )

                request.session['basket'] = []
                request.session.modified = True

                messages.success(request, " Sale dispatch confirmed and created successfully.")
                return redirect('logistics:create_sale_dispatch_item', dispatch_id=sale_shipment_id.id)

        except Exception as e:
            messages.error(request, f"An error occurred while confirming the dispatch: {str(e)}")
            return redirect('logistics:create_sale_dispatch_item', dispatch_id=sale_shipment_id.id)

    return render(request, 'logistics/sales/confirm_sale_dispatch_item.html', {'basket': basket})





@login_required
def sale_dispatch_item_list(request, sale_order_id):
    sale_order = get_object_or_404(SaleOrder, id=sale_order_id)
    dispatch_items = SaleDispatchItem.objects.filter(dispatch_item__sale_order=sale_order)

    product_wise_totals = defaultdict(lambda: {
        'order_quantity': 0,
        'dispatch_quantity': 0,
        'good_quantity': 0,
        'bad_quantity': 0
    })

    shipments = {}
    qc_quantities = {} 

    for dispatch_item in dispatch_items:
        shipment = dispatch_item.sale_shipment
        product_name = dispatch_item.dispatch_item.product.name
        if shipment not in shipments:
            shipments[shipment] = []
        shipments[shipment].append(dispatch_item)

        product_wise_totals[product_name]['order_quantity'] += dispatch_item.dispatch_item.quantity or 0
        product_wise_totals[product_name]['dispatch_quantity'] += dispatch_item.dispatch_quantity or 0

        qc_entry = SaleQualityControl.objects.filter(sale_dispatch_item=dispatch_item.dispatch_item.product.id).first()
        if qc_entry:
            good_quantity = qc_entry.good_quantity or 0
            bad_quantity = qc_entry.bad_quantity or 0

            product_wise_totals[product_name]['good_quantity'] += good_quantity
            product_wise_totals[product_name]['bad_quantity'] += bad_quantity

            qc_quantities[dispatch_item.id] = {
                'good_quantity': good_quantity,
                'bad_quantity': bad_quantity,
                'created_at': qc_entry.created_at
            }
        else:
            product_wise_totals[product_name]['good_quantity'] += 0
            product_wise_totals[product_name]['bad_quantity'] += 0

    context = {
        'sale_order': sale_order,
        'shipments': shipments,
        'product_wise_totals': dict(product_wise_totals),
        'qc_quantities': qc_quantities,    }

    return render(request, 'logistics/sales/dispatch_item_list.html', context)





def update_sale_dispatch_status(request, dispatch_item_id):
    dispatch_item = get_object_or_404(SaleDispatchItem, id=dispatch_item_id)
    if request.method == 'POST':
        new_status = request.POST.get('new_status')
        dispatch_item.status = new_status
        dispatch_item.save()

    shipment = dispatch_item.sale_shipment
    shipment.update_shipment_status()

    return redirect('logistics:sale_dispatch_item_list', sale_order_id=shipment.sales_order.id)



def cancel_sale_dispatch_item(request, dispatch_item_id):
    dispatch_item = get_object_or_404(SaleDispatchItem, id=dispatch_item_id)

    if request.method == "POST":
        dispatch_item.status = 'CANCELLED'
        dispatch_item.save()
        messages.success(request, "Dispatch item successfully cancelled.")

        return redirect('logistics:cancel_sale_dispatch_item', dispatch_item_id=dispatch_item.id)      
    return render(request, 'logistics/sales/cancel_order_item.html', {'dispatch_item': dispatch_item})




