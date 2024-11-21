

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.db import transaction
import uuid
from django.db.models import Sum
from django.db import IntegrityError



from sales.models import SaleOrder
from.models import ReturnOrRefund,FaultyProduct, Replacement
from .forms import ReturnOrRefundForm,ReplacementProductForm,ReturnOrRefundFormInternal
from inventory.models import Inventory
from django.utils import timezone
from.forms import FaultyProductForm,ReturnOrRefundForm,ReplacementProductForm,ReturnOrRefundFormInternal

from django.core.paginator import Paginator

from sales.models import SaleOrder


def repair_return_dashboard(request):
    return render(request,'repairreturn/dashboard.html')

def sale_order_list(request):
    sale_orders = SaleOrder.objects.all()
    return render(request, 'repairreturn/sale_order_list.html',{'sale_orders':sale_orders})


from sales.models import SaleOrderItem

def create_return_request(request, sale_order_id):
    sale_order = get_object_or_404(SaleOrder, id=sale_order_id)
    sales = sale_order.sale_order.all() 
 
    return_requests = ReturnOrRefund.objects.prefetch_related('faulty_products__faulty_replacement').all()
   
    if request.method == 'POST':
        form = ReturnOrRefundForm(request.POST)
   

        sale_id = request.POST.get('sale')
        sale = get_object_or_404(SaleOrderItem, id=sale_id)

        if form.is_valid():
            return_refund = form.save(commit=False)
            return_refund.sale = sale
            return_refund.save()
            messages.success(request, 'Return/Refund request submitted successfully!')
            return redirect('repairreturn:sale_order_list')  
    else:
        form = ReturnOrRefundForm()


    paginator =Paginator(return_requests,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'repairreturn/refund_return//user_create_return_request.html', {
        'form': form,
        'sale_order': sale_order,
        'sales': sales,
        'return_requests':return_requests,
         'page_obj':page_obj
    })





def return_request_list(request):
    returns = ReturnOrRefund.objects.all()

    paginator =Paginator(returns ,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'repairreturn/refund_return//user_return_request_list.html', {'page_obj': page_obj})




def manage_return_request(request, return_id):
    return_request = get_object_or_404(ReturnOrRefund, id=return_id)

    if request.method == 'POST':
        form = ReturnOrRefundFormInternal(request.POST, instance=return_request)
        if form.is_valid():
            return_request = form.save(commit=False)
            return_request.processed_by = request.user
            return_request.processed_date = timezone.now()

            if return_request.status == 'Acknowledged' and return_request.return_reason == 'DEFECTIVE':
                FaultyProduct.objects.create(
                    sale=return_request.sale,
                    product=return_request.sale.product,
                    faulty_product_quantity=return_request.quantity_refund,
                    reason_for_fault=return_request.return_reason,  
                    inspected_by=request.user  
                )
            
            return_request.save()
            messages.success(request, f'{return_request.sale.product.name} has been processed.')
            return redirect('repairreturn:return_request_list') 
    else:
        form = ReturnOrRefundFormInternal(instance=return_request)

    return render(request, 'repairreturn/refund_return/manage_return_request.html', {
        'form': form,
        'return_request': return_request
    })



def faulty_product_list(request):
    faulty_products = FaultyProduct.objects.all()

    paginator = Paginator(faulty_products,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number
                                  )
    return render(request, 'repairreturn/refund_return//faulty_product_list.html', 
    {
        'faulty_products':faulty_products,
        'page_obj':page_obj
     })



def repair_faulty_product(request, faulty_product_id):
    faulty_product = get_object_or_404(FaultyProduct, id=faulty_product_id)
    if request.method == 'POST':
        form = FaultyProductForm(request.POST, instance=faulty_product)
        if form.is_valid():
            faulty_product = form.save(commit=False)                               
            faulty_product.save()

            messages.success(request, f'{faulty_product.product.name} has been processed.')
            return redirect('repairreturn:faulty_product_list')  
    else:
        form = FaultyProductForm(instance=faulty_product)

    return render(request, 'repairreturn/refund_return/repair_faulty_product.html', {
        'faulty_product': faulty_product,
        'form': form
    })

from inventory.models import Inventory,InventoryTransaction

def replacement_return_repaired_product(request, faulty_product_id):
    faulty_product = get_object_or_404(FaultyProduct, id=faulty_product_id)
    
    if request.method == 'POST':
        form = ReplacementProductForm(request.POST)
        if form.is_valid():
            replacement = form.save(commit=False)
            replacement.customer = faulty_product.sale.sale_order.customer
            replacement.user = request.user
            
            if faulty_product.status in ['UNREPAIRABLE', 'SCRAPPED']:
                calculated_replacement_qty = faulty_product.faulty_product_quantity - (faulty_product.repair_quantity or 0)
                
                if calculated_replacement_qty > 0:
                    replacement.replacement_quantity = calculated_replacement_qty                   
        
                    try:
                        inventory_transaction = InventoryTransaction.objects.create(
                            product=faulty_product.sale.product,
                            warehouse=faulty_product.sale.warehouse,
                            transaction_type='REPLACEMENT_OUT',
                            quantity=calculated_replacement_qty,
                            remarks=f"Replacement for Faulty Product ID {faulty_product.id}"
                        )
                        
                        # Check if inventory can support the transaction
                        if inventory_transaction.update_inventory():  # Assume update_inventory checks stock and updates.
                            replacement.faulty_product = faulty_product
                            replacement.save()
                            messages.success(request, "Replacement process successfully completed and inventory updated.")
                            return redirect('repairreturn:faulty_product_list')
                        else:
                            inventory_transaction.delete()  # Rollback the transaction
                            messages.warning(request, "Not enough stock in the inventory for replacement.")
                            return redirect('repairreturn:faulty_product_list')
                    
                    except Exception as e:
                        messages.error(request, f"An error occurred: {e}")
                        return redirect('repairreturn:faulty_product_list')
                
                else:
                    messages.warning(request, "Item has already been processed for repair/replacement.")
                    return redirect('repairreturn:faulty_product_list')
            
            elif faulty_product.status == 'REPAIRED':
                messages.warning(request, "Item has been repaired, so a replacement cannot be made.")
                return redirect('repairreturn:faulty_product_list')
                
            else:
                messages.warning(request, "Unexpected product status for replacement.")
                return redirect('repairreturn:faulty_product_list')
                
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = ReplacementProductForm()
    
    return render(request, 'repairreturn/refund_return/return_repaired_faulty_product.html', {
        'form': form,
        'faulty_product': faulty_product
    })



def replacement_product_list(request):
    replacement_products =Replacement.objects.all()

    paginator = Paginator(replacement_products,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'repairreturn/refund_return//replacement_product_list.html', {
    
    'replacement_products':replacement_products,
    'page_obj':page_obj
    
    })

