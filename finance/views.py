
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from logistics.models import PurchaseShipment,SaleShipment
from sales.models import SaleOrder
from purchase.models import PurchaseOrder
from .models import PurchaseInvoice,SaleInvoice, PurchasePayment,SalePayment
from .forms import PurchaseInvoiceForm, PurchasePaymentForm,SaleInvoiceForm,SalePaymentForm

from django.db.models import Sum



@login_required
def create_purchase_invoice(request, order_id):
    purchase_shipment = get_object_or_404(PurchaseShipment, id=order_id) 

    if purchase_shipment.shipment_invoices.count() > 0:
        if purchase_shipment.shipment_invoices.filter(status__in=['SUBMITTED', 'PARTIALLY_PAYMENT', 'FULLY_PAYMENT']).count() == purchase_shipment.shipment_invoices.count():
            messages.error(request, "All invoices for this shipment have already been submitted or paid.")
            return redirect('purchase:purchase_order_list')
    else:
         pass     

    try:       
        if purchase_shipment.status != 'DELIVERED':
            messages.error(request, "Cannot create an invoice: Shipment status is not 'Delivered yet'.")
            return redirect('purchase:purchase_order_list') 
    except PurchaseShipment.DoesNotExist:
        messages.error(request, "Cannot create an invoice: No shipment found for this order.")
        return redirect('purchase:purchase_order_list') 

    initial_data = {
        'purchase_shipment': purchase_shipment,
        'amount_due': purchase_shipment.purchase_order.total_amount
    }

    if request.method == 'POST':
        form = PurchaseInvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.user = request.user
            invoice.status ='SUBMITTED'
            invoice.save()
            messages.success(request, "Invoice created and submitted successfully.")
            return redirect('purchase:purchase_order_list')  
        else:
            messages.error(request, "Error creating invoice.")
    else:
        form = PurchaseInvoiceForm(initial=initial_data)
    return render(request, 'finance/purchase/create_invoice.html', {'form': form})




@login_required
def create_purchase_payment(request, invoice_id):
    invoice = get_object_or_404(PurchaseInvoice, id=invoice_id)
    
    # Allow payment if the invoice is SUBMITTED or PARTIALLY_PAID
    if invoice.status not in ["SUBMITTED", "PARTIALLY_PAID"]:
        messages.error(request, "Cannot create a payment: Invoice is not submitted or partially paid.")
        return redirect('purchase:purchase_order_list')

    remaining_balance = invoice.remaining_balance

    if request.method == 'POST':
        form = PurchasePaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.purchase_invoice = invoice
            payment.user = request.user

            # Ensure payment amount does not exceed remaining balance
            if payment.amount > remaining_balance:
                messages.error(request, f"Payment cannot exceed the remaining balance of {remaining_balance}.")
                return redirect('finance:create_purchase_payment', invoice_id=invoice.id)

            # Update payment status based on amount
            if payment.amount < remaining_balance:
                payment.status = "PARTIALLY_PAID"
            else:
                payment.status = "FULLY_PAID"
            
            # Save the payment
            payment.save()

            # Update invoice status based on total payments made
            if invoice.is_fully_paid:
                invoice.status = "FULLY_PAID"
            elif invoice.remaining_balance > 0:
                invoice.status = "PARTIALLY_PAID"
            invoice.save()

            messages.success(request, "Payment created successfully.")
            return redirect('finance:purchase_invoice_list')
    else:
        form = PurchasePaymentForm(initial={'purchase_invoice': invoice})

    return render(request, 'finance/purchase/create_payment.html', {
        'form': form,
        'invoice': invoice,
        'remaining_balance': remaining_balance
    })




@login_required
def purchase_invoice_list(request):
    invoices = PurchaseInvoice.objects.annotate(total_paid=Sum('purchase_payment_invoice__amount'))
    return render(request, 'finance/purchase/invoice_list.html', {'invoices': invoices})


def purchase_invoice_detail(request, invoice_id):
    invoice = get_object_or_404(PurchaseInvoice, id=invoice_id)
    payments = invoice.purchase_payment_invoice.all() 
    return render(request, 'finance/purchase/invoice_details.html', {
        'invoice': invoice,
        'payments': payments,
    })



# ###########################sale invoices #################################################################

@login_required
def create_sale_invoice(request, order_id):
    sale_shipment = get_object_or_404(SaleShipment, id=order_id)
    if sale_shipment.sale_shipment_invoices.filter(status__in=['SUBMITTED', 'FULLY_PAID', 'PARTIALLY_PAID']).exists():
        messages.error(request, "All invoices for this shipment have already been submitted or paid.")
        return redirect('sales:sale_order_list')

    if sale_shipment.status != 'DELIVERED':
        messages.error(request, "Cannot create an invoice: Shipment status is not 'Delivered' yet.")
        return redirect('sales:sale_order_list')
    
    initial_data = {
        'sale_shipment': sale_shipment,
        'amount_due': sale_shipment.sales_order.total_amount
    }

    if request.method == 'POST':
        form = SaleInvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.user = request.user
            invoice.status = 'SUBMITTED'
            invoice.save()
            messages.success(request, "Invoice created and submitted successfully.")
            return redirect('sales:sale_order_list')  
    else:
        form = SaleInvoiceForm(initial=initial_data)
    
    return render(request, 'finance/sales/create_invoice.html', {'form': form})



@login_required
def create_sale_payment(request, invoice_id):
    invoice = get_object_or_404(SaleInvoice, id=invoice_id)

    if invoice.status != "SUBMITTED":
        messages.error(request, "Cannot create a payment: Invoice is not submitted yet.")
        return redirect('sales:sale_order_list')

    remaining_balance = invoice.remaining_balance

    if request.method == 'POST':
        form = SalePaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.sale_invoice = invoice       
            payment.user = request.user

            if payment.amount > remaining_balance:
                messages.error(request, f"Payment cannot exceed the remaining balance of {remaining_balance}.")
                return redirect('sales:create_sale_payment', invoice_id=invoice.id)

            if payment.amount < remaining_balance:
                payment.status = "PARTIALLY_PAID"
            else:
                payment.status = "FULLY_PAID"
            
            payment.save()

            invoice.status = "FULLY_PAID" if invoice.is_fully_paid else "PARTIALLY_PAID"
            invoice.save()

            messages.success(request, "Payment created successfully.")
            return redirect('sales:sale_invoice_list')
    else:
        form = SalePaymentForm(initial={'sale_invoice': invoice})

    return render(request, 'finance/sales/create_payment.html', {
        'form': form,
        'invoice': invoice,
        'remaining_balance': remaining_balance
    })


@login_required
def sale_invoice_list(request):
    invoices = SaleInvoice.objects.annotate(total_paid=Sum('sale_payment_invoice__amount'))
    return render(request, 'finance/sales/invoice_list.html', {'invoices': invoices})
  
   

def sale_invoice_detail(request, invoice_id):
    invoice = get_object_or_404(SaleInvoice, id=invoice_id)
    payments = invoice.sale_payment_invoice.all()  

    return render(request, 'finance/sales/invoice_details.html', {
        'invoice': invoice,
        'payments': payments,
    })



