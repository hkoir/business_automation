from django.shortcuts import render,redirect,get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from utils import create_notification
from django.utils import timezone
from datetime import datetime, timedelta
from collections import defaultdict
from django.utils.timezone import localtime
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from utils import update_sale_order,update_sale_shipment_status,update_sale_request_order
from django.contrib.auth.decorators import login_required
from django.db import transaction


from repairreturn.models import ReturnOrRefund
from repairreturn.forms import ReturnOrRefundForm,RepairReturnCustomerFeedbackForm

from recruitment.models import Job,Candidate,TakeExam,Exam
from recruitment.forms import SearchApplicationForm,TakeExamForm

from tasks.forms import CustomerUpdateTicketForm,TicketForm
from tasks.models import TeamMember,PerformanceEvaluation,TaskMessageReadStatus,Ticket,Task

from.forms import QualityControlFormByCustomer,CandidateForm
from sales.models import SaleOrder,SaleOrderItem,SaleQualityControl

from.forms import FilterForm,TicketCustomerFeedbackForm
from core.forms import CommonFilterForm
from logistics.models import SaleDispatchItem,SaleShipment
from recruitment.models import  Candidate
from clients.models import SubscriptionPlan




def partner_landing_page(request):
    return render(request,'customerportal/partner_landing_page.html')


def public_landing_page(request):
    plans = SubscriptionPlan.objects.all().order_by('duration')
    for plan in plans:
        plan.features_list = plan.features.split(',') if plan.features else [] 
    return render(request,'customerportal/public_landing_page.html',{'plans':plans})


def job_landing_page(request):
    return render(request,'customerportal/recruitment/job_landing_page.html')



@login_required
def sale_order_list(request):
    sale_order_number=None
    form = CommonFilterForm(request.GET or None)
    sale_orders = SaleOrder.objects.all().order_by('-created_at')
        
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Customer').exists():
            sale_orders = sale_orders.filter(user = request.user)
        else:
            sale_orders = sale_orders


    if form.is_valid():
        sale_order_number = form.cleaned_data['sale_order_id']
        if sale_order_number:
            sale_orders = sale_orders.filter(order_id = sale_order_number)
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field.capitalize()}: {error}")

    paginator = Paginator(sale_orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form=CommonFilterForm()

    return render(request, 'customerportal/sale_order_list.html',
        {
            'sale_orders':sale_orders,
            'form':form,
            'sale_order_number':sale_order_number,
            'page_obj':page_obj,
            'sale_order_number':sale_order_number
        })




def item_dispatched(request,sale_order_id):
    sale_order = get_object_or_404(SaleOrder, id=sale_order_id)
    dispatch_items = SaleDispatchItem.objects.filter(dispatch_item__sale_order=sale_order)

    product_wise_totals = defaultdict(lambda: {
        'order_quantity': 0,
        'dispatch_quantity': 0,
        'good_quantity_by_customer': 0,
        'bad_quantity_by_customer': 0
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

        qc_entry = dispatch_item.sale_quality_control.first()
        if qc_entry:
            good_quantity = qc_entry.good_quantity_by_customer or 0
            bad_quantity = qc_entry.bad_quantity_by_customer or 0

            product_wise_totals[product_name]['good_quantity_by_customer'] += good_quantity
            product_wise_totals[product_name]['bad_quantity_by_customer'] += bad_quantity

            qc_quantities[dispatch_item.id] = {
                'good_quantity_by_customer': good_quantity,
                'bad_quantity_by_customer': bad_quantity,
                'created_at': qc_entry.created_at
            }
          
        else:
            product_wise_totals[product_name]['good_quantity_by_customer'] += 0
            product_wise_totals[product_name]['bad_quantity_by_customer'] += 0

    context = {
        'sale_order': sale_order,
        'shipments': shipments,
        'product_wise_totals': dict(product_wise_totals),
        'qc_quantities': qc_quantities,    }
    return render(request, 'customerportal/item_dispatch.html', context)



@login_required
def sale_dispatch_item_list(request, sale_order_id):  
    sale_order = get_object_or_404(SaleOrder, id=sale_order_id)
    dispatch_items = SaleDispatchItem.objects.filter(dispatch_item__sale_order=sale_order)

    product_wise_totals = defaultdict(lambda: {
        'order_quantity': 0,
        'dispatch_quantity': 0,
        'good_quantity_by_customer': 0,
        'bad_quantity_by_customer': 0
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

        qc_entry = dispatch_item.sale_quality_control.first()
        if qc_entry:
            good_quantity = qc_entry.good_quantity_by_customer or 0
            bad_quantity = qc_entry.bad_quantity_by_customer or 0

            product_wise_totals[product_name]['good_quantity_by_customer'] += good_quantity
            product_wise_totals[product_name]['bad_quantity_by_customer'] += bad_quantity

            qc_quantities[dispatch_item.id] = {
                'good_quantity_by_customer': good_quantity,
                'bad_quantity_by_customer': bad_quantity,
                'created_at': qc_entry.created_at
            }
          
        else:
            product_wise_totals[product_name]['good_quantity_by_customer'] += 0
            product_wise_totals[product_name]['bad_quantity_by_customer'] += 0

    context = {
        'sale_order': sale_order,
        'shipments': shipments,
        'product_wise_totals': dict(product_wise_totals),
        'qc_quantities': qc_quantities,    }
    return render(request, 'customerportal/dispatch_item_list.html', context)



@login_required
def update_sale_dispatch_status(request, dispatch_item_id):
    dispatch_item = get_object_or_404(SaleDispatchItem, id=dispatch_item_id)          
    
    if request.method == 'POST':
        if dispatch_item.status in ['OBI','DELIVERED']:
            messages.info(request,'item has already been updated')
            return redirect('customerportal:update_sale_dispatch_status',dispatch_item_id)
        
        new_status = request.POST.get('new_status')
        old_status = dispatch_item.status
        dispatch_item.status = new_status
        dispatch_item.save()
        create_notification(request.user, message=f'Product: {dispatch_item.dispatch_item.product} status updated from {old_status} to {new_status}',notification_type='SHIPMENT-NOTIFICATION')     

    shipment = dispatch_item.sale_shipment
    shipment.update_shipment_status()
    try:
        shipment = SaleShipment.objects.get(id=shipment.id)

        total_dispatch_items = shipment.sale_shipment_dispatch.count()
        reached_items_count = shipment.sale_shipment_dispatch.filter(status__in=['REACHED', 'OBI']).count()

        all_items_reached = reached_items_count == total_dispatch_items

        if all_items_reached:
            shipment.status = 'REACHED'
            shipment.sales_order.status = 'REACHED'
            shipment.save()            

            print(f"Shipment {shipment.id} marked as REACHED.")

            for dispatch_item in shipment.sale_shipment_dispatch.filter(status__in=['REACHED', 'OBI']):
                create_notification(request.user, message=f'Item { dispatch_item.dispatch_item.product} has just reached',notification_type='SHIPMENT-NOTIFICATION')

    except SaleShipment.DoesNotExist:
        print(f"Shipment {shipment.id} not found.")   
    return redirect('customerportal:sale_dispatch_item_list', sale_order_id=shipment.sales_order.id)




@login_required
def customer_qc_dashboard(request, sale_order_id=None):
    if sale_order_id:
        pending_items = SaleDispatchItem.objects.filter(
            sale_shipment__sales_order=sale_order_id,
            status__in=['REACHED', 'OBI']
        )
        if not pending_items:
             messages.info(request, "No items pending for quality control inspection.No new goods arrived yet")
            
        sale_order = get_object_or_404(SaleOrder, id=sale_order_id)
    else:
        pending_items = SaleDispatchItem.objects.filter(status__in=['REACHED', 'OBI'])
        sale_order = None
        if not pending_items:
            messages.info(request, "No items pending for quality control inspection.No new goods arrived yet")               
    return render(request, 'customerportal/customer_qc_dashboard.html', {'pending_items': pending_items, 'sale_order': sale_order})




@login_required
def customer_qc_inspect_item(request, item_id):
    sale_dispatch_item = get_object_or_404(SaleDispatchItem, id=item_id)   
    sale_order = sale_dispatch_item.dispatch_item.sale_order
    sale_request_order = sale_order.sale_request_order
    sale_shipment = sale_dispatch_item.sale_shipment   
    sale_order_item = sale_dispatch_item.dispatch_item
    sale_request_item = sale_order_item.sale_request_item
   

    if not sale_shipment:
        messages.error(request, "No shipment found for this order item.")
        return redirect('customerportal:customer_qc_dashboard')  
    if not sale_dispatch_item.status in ['REACHED','OBI']:
        messages.error(request, "Goods not arrived yet found for this order item.")
        return redirect('customerportal:customer_qc_dashboard')  
    
    if sale_shipment.status != 'REACHED':
                messages.info(request, "Cannot inspect due to delivery has not been done yet.")
                return redirect('customerportal:customer_qc_dashboard')

    if request.method == 'POST':
        try:
            qc_entry = SaleQualityControl.objects.get(sale_dispatch_item=sale_dispatch_item)  # Assuming sale_dispatch_item is unique
            form = QualityControlFormByCustomer(request.POST, instance=qc_entry) # Bind to existing instance
        except QualityControl.DoesNotExist:           
            form = QualityControlFormByCustomer(request.POST)
       
        if form.is_valid():           
            qc_entry = form.save(commit=False)
            qc_entry.sale_dispatch_item = sale_dispatch_item
            qc_entry.user = request.user 
            qc_entry.quality_check_by = 'BY-CUSTOMER' 
            qc_entry.inspection_date_by_customer = timezone.now()
            qc_entry.save()

            sale_dispatch_item.status = 'DELIVERED' # status changed from READY-FOR-DISPATCH >> DISPATCHED >> REACHED >> DELIVERED
            sale_dispatch_item.save()               
           
            sale_order_item.status ='DELIVERED'
            sale_order_item.save()

            sale_request_item.status ='DELIVERED'
            sale_request_item.save()

            update_sale_order(sale_order.id)      
            update_sale_shipment_status(sale_shipment.id)
            update_sale_request_order(sale_request_order.id)      
            sale_shipment.update_shipment_status()   
                 
            messages.success(request, "Quality control inspection recorded successfully.")
            return redirect('customerportal:customer_qc_dashboard')
        else:
            messages.error(request, "Error saving QC inspection.")
    else:
        form = QualityControlFormByCustomer(initial={'total_quantity': sale_dispatch_item.dispatch_quantity})    
    return render(request, 'customerportal/customer_qc_inspect_item.html', {'form': form, 'sale_dispatch_item': sale_dispatch_item})

######################### Supplier ###################################################
from purchase.models import PurchaseOrder
from purchase.forms import PurchaseOrderSearchForm
from purchase.models import QualityControl
from django.db.models import Sum


@login_required
def purchase_order_list(request):
    purchase_order = None
    purchase_orders = PurchaseOrder.objects.all().order_by("-created_at")

    form = CommonFilterForm(request.GET or None)
    if form.is_valid():
        purchase_order = form.cleaned_data['purchase_order_id']
        if purchase_order:
            purchase_orders = purchase_orders.filter(order_id=purchase_order)
    
   
    paginator = Paginator(purchase_orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'customerportal/purchase/purchase_order_list.html', {
        'purchase_orders': purchase_orders,           
        'user': request.user,
        'form': form,
        'page_obj': page_obj,
        'purchase_order': purchase_order,
       
    })

@login_required
def purchase_order_items(request,order_id):
    order_instance = get_object_or_404(PurchaseOrder,id=order_id)
    return render(request,'customerportal/purchase/purchase_order_items.html',{'order_instance':order_instance})



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

    return render(request, 'customerportal/purchase/dispatch_item_list.html', context)

from logistics.models import PurchaseDispatchItem
from shipment.models import PurchaseShipment

@login_required
def update_dispatch_status(request, dispatch_item_id):
    dispatch_item = get_object_or_404(PurchaseDispatchItem, id=dispatch_item_id)
    if request.method == 'POST':
        new_status = request.POST.get('new_status')
        old_status = dispatch_item.status
        dispatch_item.status = new_status
        dispatch_item.save()  
        create_notification(request.user, message=f'Product: {dispatch_item.dispatch_item.product} status updated from {old_status} to {new_status}',notification_type='SHIPMENT-NOTIFICATION')     

    shipment = dispatch_item.purchase_shipment
    shipment.update_shipment_status()

    try:
        shipment = PurchaseShipment.objects.get(id=shipment.id)

        total_dispatch_items = shipment.shipment_dispatch_item.count()
        reached_items_count = shipment.shipment_dispatch_item.filter(status__in=['REACHED', 'OBI']).count()

        all_items_reached = reached_items_count == total_dispatch_items

        if all_items_reached:
            shipment.status = 'REACHED'
            shipment.purchase_order.status = 'REACHED'
            shipment.save()

            for dispatch_item in shipment.shipment_dispatch_item.filter(status__in=['REACHED', 'OBI']):
                create_notification(request.user, message=f'Item {dispatch_item.dispatch_item.product} has just reached',notification_type='SHIPMENT-NOTIFICATION')

    except PurchaseShipment.DoesNotExist:
        print(f"Shipment {shipment.id} not found.")


    return redirect('customerportal:dispatch_item_list', purchase_order_id=shipment.purchase_order.id)




def cancel_dispatch_item(request, dispatch_item_id):
    dispatch_item = get_object_or_404(PurchaseDispatchItem, id=dispatch_item_id)

    if request.method == "POST":
        dispatch_item.status = 'CANCELLED'
        dispatch_item.save()
        messages.success(request, "Dispatch item successfully cancelled.")

        return redirect('logistics:dispatch_item_list', purchase_order_id=dispatch_item.dispatch_item.purchase_order.id)
    return render(request, 'logistics/purchase/cancel_order_item.html', {'dispatch_item': dispatch_item})



from finance.models import PurchaseInvoice
from finance.forms import PurchaseInvoiceForm,PurchaseInvoiceAttachmentForm

@login_required
def create_purchase_invoice(request, order_id):
    purchase_shipment = get_object_or_404(PurchaseShipment, id=order_id) 

    if purchase_shipment.shipment_invoices.count() > 0:
        if purchase_shipment.shipment_invoices.filter(status__in=['SUBMITTED', 'PARTIALLY_PAYMENT', 'FULLY_PAYMENT']).count() == purchase_shipment.shipment_invoices.count():
            messages.error(request, "All invoices for this shipment have already been submitted or paid.")
            return redirect('customerportal:purchase_order_list')
    else:
         pass     

    try:       
        if purchase_shipment.status != 'DELIVERED':
            messages.error(request, "Cannot create an invoice: Shipment status is not 'Delivered yet'.")
            return redirect('purchase:purchase_order_list') 
    except PurchaseShipment.DoesNotExist:
        messages.error(request, "Cannot create an invoice: No shipment found for this order.")
        return redirect('customerportal:purchase_order_list') 

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
            return redirect('customerportal:purchase_order_list')  
        else:
            messages.error(request, "Error creating invoice.")
    else:
        form = PurchaseInvoiceForm(initial=initial_data)
    return render(request, 'customerportal/purchase/create_invoice.html', {'form': form})


@login_required
def add_purchase_invoice_attachment(request, invoice_id):
    invoice = get_object_or_404(PurchaseInvoice, id=invoice_id)    
    if request.method == 'POST':
        form = PurchaseInvoiceAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.purchase_invoice = invoice  
            attachment.user=request.user
            attachment.save()
            return redirect('customerportal:purchase_order_list')
    else:
        form = PurchaseInvoiceAttachmentForm()

    return render(request, 'customerportal/purchase/add_invoice_attachment.html', {'form': form, 'invoice': invoice})



#######################################################################################


def create_ticket(request):    
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            priority = form.cleaned_data['priority']            
            ticket= form.save(commit=False)
            ticket.created_by = request.user
            ticket.user=request.user
            ticket.save()           

            task = Task.objects.create(
                ticket=ticket,  
                progress=0.0,
                user=request.user,
                task_type='TICKET',
                title='Ticket',
                priority = priority
            )

            messages.success(request, 'Ticket and task  created successfully!')

            create_notification(request.user,message=f"A ticket with task '{ticket.subject}' has been created",notification_type='TICKET-NOTIFICATION')
            return redirect('customerportal:ticket_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
   
    form = TicketForm()
    return render(request, 'customerportal/create_ticket.html', {'form': form})




def ticket_list(request):   
    form = FilterForm(request.GET)
    tickets = Ticket.objects.all().order_by('-created_at') 
   
    unread_messages = defaultdict(list) 
    unread_statuses = TaskMessageReadStatus.objects.filter(user=request.user, read=False)
    for status in unread_statuses:
        unread_messages[status.task_message.task.id].append(status.task_message)
      
       
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Customer').exists():
            tickets = tickets.filter(user = request.user)
        else:
            tickets = tickets


    if request.method == 'GET':
        form = FilterForm(request.GET)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            ticket_number = form.cleaned_data['ticket_number']
            
            if start_date and end_date:
                tickets =  tickets.filter(created_at__range=(start_date, end_date))  
            if ticket_number:           
                tickets =  tickets.filter(ticket_id = ticket_number)    
        else:
            print(form.errors)
            form = FilterForm()
   
    paginator = Paginator(tickets, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = FilterForm()
    return render(request, 'customerportal/tickets_list.html', {'form': form,'page_obj':page_obj,'unread_messages':unread_messages})


def update_ticket(request, ticket_id):    
    ticket = get_object_or_404(Ticket, id=ticket_id)
    sale_return =None

# when update ticket at the same time we will update repair return object and task object

# Fetch repair return variables to update repair return object##################
    try:           
        sale_order = ticket.sales           
        if not sale_order:
            messages.info(request,'there is an error of fetching related field')
            raise AttributeError("No Sale Order found for the task ticket.")

        sale_order_item = sale_order.sale_order.first()            
        if not sale_order_item :
            messages.info(request,'there is an error of fetching related field')
            raise AttributeError("No Sale Returns found for the Sale Order.") 
        sale_return = sale_order_item.sale_returns.first()              
                                
    except AttributeError as e:
        messages.info(request,'there is an error of fetching related field')
        print(f"Error: {str(e)}")  
   

    if request.method == 'POST':
        form = CustomerUpdateTicketForm(request.POST, instance=ticket)  
        if form.is_valid():     
            customer_feedback = form.cleaned_data['customer_feedback']
            form = form.save(commit=False) 

            if customer_feedback == 'PROGRESS-100%':
                messages.success(request, f'Ticket have completed, can not update anymore')
                        
# update ticket data and repair return data ####################
            if customer_feedback == 'PROGRESS-20%':
                form.progress_by_customer = 20.0 # update ticket object
                sale_return.progress_by_customer = 20.0 # update repair return object object
            elif form.customer_feedback == 'PROGRESS-30%':
                form.progress_by_customer = 30.0
                sale_return.progress_by_customer = 30.0
            elif form.customer_feedback == 'PROGRESS-40%':
                form.progress_by_customer = 40.0
                sale_return.progress_by_customer = 40.0            
            elif customer_feedback == 'PROGRESS-50%':
                form.progress_by_customer = 50.0
                sale_return.progress_by_customer = 50.0
            elif customer_feedback == 'PROGRESS-60%':
                form.progress_by_customer = 60.0
                sale_return.progress_by_customer = 60.0
            elif customer_feedback == 'PROGRESS-70%':
               form. progress_by_customer = 70.0
               sale_return.progress_by_customer = 70.0
            elif customer_feedback == 'PROGRESS-80%':
                form.progress_by_customer = 80.0
                sale_return.progress_by_customer = 80.0
            elif customer_feedback == 'PROGRESS-90%':
                sale_return.progress_by_customer = 90.0
                form.progress_by_customer = 90.0
            elif customer_feedback == 'PROGRESS-100%':
                form.progress_by_customer = 100.0
                sale_return.progress_by_customer = 100.0
            else:
                form.progress_by_customer = 0.0
                sale_return.progress_by_customer = 0.0

            form.user = request.user
            form.save()
            sale_return.save()
           
    #############Update task data and calculate performance at the same time#############
   
            ### Update task progress
            for task in ticket.task.all():  
                task.progress = ticket.progress_by_customer  
                task.save() # task data updated #####################################

                # Calculate performance data
                new_obtained_number = task.calculate_obtained_number()
                task.obtained_number = new_obtained_number
                if task.assigned_number > 0:
                    task.obtained_score = (new_obtained_number / task.assigned_number) * 100 
                if task.progress >= 100:
                    task.status = 'COMPLETED'
                elif task.progress > 0:
                    task.status = 'IN_PROGRESS'
                else:
                    task.status = 'PENDING'
                task.save()
                if task.assigned_to_team:
                    team_members = TeamMember.objects.filter(team=task.assigned_to_team)
                    for member in team_members:
                        evaluation, created = PerformanceEvaluation.objects.get_or_create(
                            employee=member.member,
                            task=task,
                            team=task.assigned_to_team,
                            defaults={
                                'assigned_quantitative_number': 0,
                                'remarks': 'Progressive evaluation in progress.',
                            }
                        )
                        evaluation.obtained_quantitative_score = (task.obtained_number / task.assigned_number) * 100 if task.assigned_number else 0
                        evaluation.obtained_quantitative_number = task.obtained_number
                        evaluation.assigned_quantitative_number = task.assigned_number
                        evaluation.remarks = f"Progress: {task.progress}%. Updated incremental score."
                        create_notification(request.user, message= f'Task:{task.title}, progress {task.progress}% updated by {request.user} dated {timezone.now()}',notification_type='TASK-NOTIFICATION')
                        evaluation.save()
                elif task.assigned_to_employee:
                    evaluation, created = PerformanceEvaluation.objects.get_or_create(
                        employee=task.assigned_to_employee,
                        task=task,
                        defaults={
                            'assigned_quantitative_number': 0,
                            'remarks': 'Progressive evaluation in progress.',
                        }
                    )
                    evaluation.obtained_quantitative_score = task.obtained_score
                    evaluation.obtained_quantitative_number = task.obtained_number
                    evaluation.assigned_quantitative_number = task.assigned_number
                    evaluation.remarks = f"Progress: {task.progress}%. Updated incremental score."
                    evaluation.save()                            
                
                messages.success(request, f'Ticket updated successfully with feedback: {ticket.customer_feedback} complete!')
                create_notification(request.user,message= f"A ticket with subject '{ticket.subject}' has been updated", notification_type='TICKET-NOTIFICATION')
                return redirect('customerportal:ticket_list')
        
                          
        else:  
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")

    else:
        form = CustomerUpdateTicketForm(instance=ticket)
    return render(request, 'customerportal/update_ticket.html', {'form': form})




def ticket_customer_feedback(request,ticket_id):
    tickets = Ticket.objects.all().order_by('-created_at')
    ticket_instance =get_object_or_404(Ticket,id=ticket_id)     
      
    form = TicketCustomerFeedbackForm(request.POST,request.FILES,instance=ticket_instance)
    if request.method == 'POST':
        form = TicketCustomerFeedbackForm(request.POST,request.FILES,instance=ticket_instance)
        if form.is_valid():         
            is_work_completed = form.cleaned_data['is_work_completed']
            repair_ticket = form.save(commit=False)
            repair_ticket.save()

            messages.success(request,'Thanks for your feedback')
            return redirect('customerportal:return_request_list')
        else:
            messages.info(request,'form is invalid')

    paginator =Paginator(tickets ,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)  

    form = TicketCustomerFeedbackForm(
                initial={
                    'ticket':ticket_instance,  
                }
            )
    return render(request, 'customerportal/ticket_customer_feedback.html',
         {
             'page_obj': page_obj,
             'form':form,
            
             
        })



@login_required
def create_return_request(request, sale_order_id):
    sale_order = get_object_or_404(SaleOrder, id=sale_order_id)
    sales = sale_order.sale_order.all()
    return_requests = ReturnOrRefund.objects.prefetch_related('faulty_products__faulty_replacement').all()

    if request.method == 'POST':
        form = ReturnOrRefundForm(request.POST, sale_order_id=sale_order_id)  

        sale_id = request.POST.get('sale')
        try:
            sale = get_object_or_404(SaleOrderItem, id=sale_id)
        except:
            messages.error(request, "Invalid sale item selected.")
            return redirect(request.path)
        
        if form.is_valid():
            return_refund = form.save(commit=False)
            return_refund.sale = sale
            return_refund.user=request.user
            return_refund.save()

            with transaction.atomic():
                ticket = Ticket.objects.create(
                    sales=sale_order,  
                    progress_by_customer=0.0,
                    progress_by_user=0.0,
                    user=request.user,
                    ticket_type='REPAIR-RETRUN',               
                
                )

                task = Task.objects.create(
                    ticket=ticket,  
                    progress=0.0,
                    user=request.user,
                    task_type='TICKET',
                    title='Repair Return',
                
                )

            create_notification(
                request.user,
               message= f"Customer {sale_order.customer} has placed a repair/return request for: {sale.product}",
                notification_type='RETURN-NOTIFICATION'
            )
            messages.success(request, "A Task of Return/Refund request submitted successfully!")
            return redirect('customerportal:return_request_list')
        else:
            messages.error(request, "There was an error with your submission. Please check the form.")
    else:
        form = ReturnOrRefundForm(sale_order_id=sale_order_id) 

    paginator = Paginator(return_requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'customerportal/user_create_return_request.html', {
        'form': form,
        'sale_order': sale_order,
        'sales': sales,
        'return_requests': return_requests,
        'page_obj': page_obj
    })



@login_required
def return_request_progress(request, sale_order_id):
    sale_order = get_object_or_404(SaleOrder, id=sale_order_id)
    sales = sale_order.sale_order.all()  
    return_requests = ReturnOrRefund.objects.prefetch_related('faulty_products__faulty_replacement').all().order_by('-created_at')
      
    paginator =Paginator(return_requests,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'customerportal/return_request_progress.html', {
        'sale_order': sale_order,
        'sales': sales,
        'return_requests':return_requests,
        'page_obj':page_obj
    })


@login_required
def customer_return_request_list(request):
    return_id=None
    returns = ReturnOrRefund.objects.all().order_by('-created_at')
    form = CommonFilterForm(request.GET or None)
    if form.is_valid():
        return_id = form.cleaned_data['sale_order_id']
        if return_id:
            returns = returns.filter(sale__sale_order__order_id = return_id)
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field.capitalize()}: {error}")

    paginator =Paginator(returns ,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form=CommonFilterForm()
    return render(request, 'customerportal/user_return_request_list.html',
         {
             'page_obj': page_obj,
             'form':form,
             'page_obj':page_obj,
             'return_id':return_id
        })



def repair_return_customer_feedback(request,return_id):
    returns = ReturnOrRefund.objects.all().order_by('-created_at')
    return_instance =get_object_or_404(ReturnOrRefund,id=return_id)     
               
    feedback_instance = return_instance.return_feedback.first()    
    form = RepairReturnCustomerFeedbackForm(request.POST,request.FILES,instance=feedback_instance)
    if request.method == 'POST':
        form = RepairReturnCustomerFeedbackForm(request.POST,request.FILES,instance=feedback_instance)
        if form.is_valid():         
            is_work_completed = form.cleaned_data['is_work_completed']
            repair_ticket = form.save(commit=False)
            repair_ticket.save()

            messages.success(request,'Thanks for your feedback')
            return redirect('customerportal:return_request_list')
        else:
            messages.info(request,'form is invalid')

    paginator =Paginator(returns ,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)  

    form = RepairReturnCustomerFeedbackForm(
                initial={
                    'repair_return': return_instance,  
                }
            )
    return render(request, 'customerportal/customer_feedback.html',
         {
             'page_obj': page_obj,
             'form':form,
            
             
        })


####################  Job portal ##########################################################

def job_list_candidate_view(request): 
    
    jobs = Job.objects.filter(is_active = True).order_by('-created_at')
    candidates = Candidate.objects.all()
    candidate = Candidate.objects.filter(candidate=request.user).first()   
    exam_start_time = None
    exam_end_time = None

    current_time = timezone.now() 
    joining_deadline = candidate.joining_deadline.isoformat() if candidate.joining_deadline else None
    expected_joining_date = candidate.expected_joining_date.isoformat() if candidate.expected_joining_date else None
    confirmation_deadline = candidate.confirmation_deadline.isoformat() if candidate.confirmation_deadline else None

    candidate_jobs = Job.objects.filter(
        id__in=Candidate.objects.filter(candidate=request.user).values_list('applied_job_id', flat=True)
    ).order_by('-created_at')

    applied_jobs = None

    if candidate:
        applied_jobs = Candidate.objects.filter(candidate=candidate.id).values_list('applied_job_id', flat=True)

    for job in jobs:        
        if job.deadline < timezone.now().date():
            job.is_active = False
            job.save()
            
        exams = job.job_exam.all()
        for exam in exams:
            exam_start_time = localtime(exam.start_time).isoformat()
            exam_end_time = localtime(exam.end_time).isoformat()        
 
    form = SearchApplicationForm(request.GET or None)    
    if request.method == 'GET':
        form = SearchApplicationForm(request.GET or None) 
        if form.is_valid():           
            query = form.cleaned_data.get('query')
            if query:
                jobs = jobs.filter(
                    Q(title__icontains=query) |
                    Q(candidates__full_name__icontains=query) |
                    Q(candidates__email__icontains=query)
                )
            else:
                jobs =jobs
        else:
            print(form.errors)
            form = SearchApplicationForm() 
  

    form = SearchApplicationForm() 
    paginator = Paginator( candidate_jobs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render (request,'customerportal/recruitment/job_list_candidate_view.html',{
        'jobs':jobs,
        'page_obj':page_obj,
        'jobs': jobs,
        'candidates': candidates,
        'candidate': candidate,
        'applied_jobs': applied_jobs, 
        'form':form,

        'exam_start_time':  exam_start_time,
        'exam_end_time':  exam_end_time,
        'current_time': localtime(current_time).isoformat(),
        'joining_deadline': joining_deadline,
        'expected_joining_date': expected_joining_date,
        'confirmation_deadline': confirmation_deadline,
      
        })

from core.models import Position

def position_details(request,id):
    position_instance = get_object_or_404(Position,id=id)
    return render(request,'customerportal/recruitment/position_details.html',{'position_instance':position_instance})


from decimal import Decimal

def job_application(request, id):
    job = get_object_or_404(Job, id=id)
    candidate = job.candidates.filter(candidate=request.user).first()  
    if request.method == "POST":
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid(): 
            candidate_instance = form.save(commit=False)
            candidate_instance.candidate = request.user  
            candidate_instance.applied_job = job       
            candidate_instance.save()                
            form.save_m2m()   
              

            candidate_instance.cv_screening_score = Decimal(candidate_instance.calculate_cv_screening_score())
            candidate_instance.save(update_fields=['cv_screening_score'])           

            messages.success(request, "Your job application has been submitted successfully.")
            return redirect('customerportal:job_list_candidate_view')
        else:
            messages.error(request, "There was an error with your application.")
    else:
        form = CandidateForm()

    return render(request, 'customerportal/recruitment/job_application_form.html', {
        'job': job,
        'form': form,
    })





def pre_take_exam(request, exam_id, candidate_id):
    exam = get_object_or_404(Exam, id=exam_id)
    candidate = get_object_or_404(Candidate, id=candidate_id)
    current_time = timezone.now()
    
    # If the exam is starting now, redirect to the exam page
    # if current_time <= exam.start_time:
    #     return redirect('customerportal:take_exam', exam_id=exam.id, candidate_id=candidate.id)
    
    return render(request, 'customerportal/recruitment/pre_take_exam.html', {
        'exam': exam,
        'candidate': candidate,
        'exam_start_time': localtime(exam.start_time).isoformat(),
        'exam_end_time': localtime(exam.end_time).isoformat(),
        'current_time': localtime(current_time).isoformat(),
    })





def take_exam(request, exam_id, candidate_id):
    exam = get_object_or_404(Exam, id=exam_id)
    candidate = get_object_or_404(Candidate, id=candidate_id)

    # if candidate.status != 'Shortlisted':
    #     messages.info(request, "You are not shortlisted for this exam.")
    #     return redirect('recruitment:job_list')  

    current_time = timezone.now()
    # if exam.is_expired():
    #     messages.warning(request, 'The exam time has expired. You can no longer take this exam.')
    #     return redirect('recruitment:job_list')
    # if exam.start_time > current_time:
    #     messages.info(request, 'The exam has not started yet. Please wait.')
    #     return redirect('recruitment:job_list')

    questions = exam.questions.all()

    if request.method == "POST":
        form = TakeExamForm(questions, request.POST)
        if form.is_valid():
            if exam.end_time <= current_time:
                messages.warning(request, 'The exam time has expired. You cannot submit the exam paper.')
                return redirect('customerportal:job_list_candidate_view')

            total_marks = 0
            for question in questions:
                selected_option = form.cleaned_data.get(f'question_{question.id}')
                is_correct = selected_option == question.correct_answer  
                question_marks = question.marks if is_correct else 0  
                total_marks += question_marks

                TakeExam.objects.create(
                    candidate=candidate,
                    exam=exam,
                    question=question,
                    selected_option=selected_option,
                    obtained_marks=question_marks
                )

            TakeExam.objects.filter(candidate=candidate, exam=exam).update(obtained_marks=total_marks)
            candidate.status = 'EXAM-PASS' if total_marks >= exam.pass_marks else 'EXAM-FAIL'
            candidate.exam_score = total_marks
            candidate.save()   
            return redirect(reverse('customerportal:pre_take_exam', kwargs={'exam_id': exam.id, 'candidate_id': candidate.id}))
    else:
        form = TakeExamForm(questions)
    return render(request, 'customerportal/recruitment/take_exam.html', {
        'exam': exam,
        'candidate': candidate,
        'form': form,
        'exam_start_time': localtime(exam.start_time).isoformat(),
        'exam_end_time': localtime(exam.end_time).isoformat(),
        'current_time': localtime(current_time).isoformat(),
    })




def selected_candidate_job_status(request): 
    jobs = Job.objects.all().order_by('-created_at')
    candidates = Candidate.objects.filter(candidate=request.user)
    candidate = Candidate.objects.filter(candidate=request.user).first()
    exam_start_time = None
    exam_end_time = None
    current_time = timezone.now()   

    for job in jobs:        
        if job.deadline < timezone.now().date():
            job.is_active = False
            job.save()
            
        exams = job.job_exam.all()
        for exam in exams:
            exam_start_time = localtime(exam.start_time).isoformat()
            exam_end_time = localtime(exam.end_time).isoformat()

            if exam.is_expired():
                messages.warning(request, 'The exam time has expired.')
            elif exam.start_time > current_time:
                messages.info(request, 'The exam has not started yet')

 
    form = SearchApplicationForm(request.GET or None)    
    if request.method == 'GET':
        form = SearchApplicationForm(request.GET or None) 
        if form.is_valid():
            print('form valid')
            query = form.cleaned_data.get('query')
            if query:
                jobs = jobs.filter(
                    Q(title__icontains=query) |
                    Q(candidates__full_name__icontains=query) |
                    Q(candidates__email__icontains=query)
                )
            else:
                jobs = jobs 
        else:
            print(form.errors,'...............form error')
            form = SearchApplicationForm() 
    else:
        print('error in get/post')

    form = SearchApplicationForm() 
    paginator = Paginator(jobs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render (request,'customerportal/recruitment/selected_candidate_job_status.html',{
        'jobs':jobs,
        'page_obj':page_obj,
         'jobs': jobs,
        'candidates': candidates,
        'candidate': candidate,
        'form':form,

        'exam_start_time':  exam_start_time,
        'exam_end_time':  exam_end_time,
        'current_time': localtime(current_time).isoformat(),
      
        })



def candidate_confirmation(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)

    # if candidate.confirmation_deadline and candidate.confirmation_deadline < timezone.now().date():
    #     messages.info(request, 'Your timing of confirmation has expired')
    #     return redirect("recruitment:selected_candidate")

    if request.method == "POST":
        decision = request.POST.get("decision")
        joining_date = request.POST.get("joining_date")
        if decision == "accept":
            candidate.offer_status = "accepted"
            candidate.confirmation_status = "accepted"
            if joining_date: 
                candidate.expected_joining_date = joining_date    
            candidate.save()            
            messages.success(request, f"Congratulation Dear Mr.{candidate.full_name}.Please meet with our hiring manager at your conveinent time within office hour")
            return redirect(reverse("recruitment:congratulations", args=[candidate.id]))
        else:
            candidate.offer_status = "declined"
            candidate.confirmation_status = "declined"
            candidate.save()
            messages.warning(request, f"{candidate.full_name} has declined the offer.")

        
       
        return redirect("recruitment:selected_candidate")  
    return render(request, "customerportal/recruitment/candidate_confirmation.html", {"candidate": candidate})
  

def congratulations(request, candidate_id):
    #candidate = get_object_or_404(Candidate, id=candidate_id, confirmation_status="accepted")
    candidate = get_object_or_404(Candidate, id=candidate_id)

    guidelines = [
        "Meet the hiring manager on your joining date.",
        "Bring original copies of your documents (ID proof, academic certificates, etc.).",
        "Sign the employment contract upon arrival.",
        "Complete your HR formalities and onboarding process.",
    ]
    return render(request, "customerportal/congratulations.html", {"candidate": candidate, "guidelines": guidelines})







from io import BytesIO
import base64
from core.models import Employee
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,letter

def generate_offer_letter_pdf(candidate, employee):
    buffer = BytesIO()
    pdf_canvas = canvas.Canvas(buffer, pagesize=A4)

    margin = 50
    line_height = 15
    y_position = 700  
    pdf_canvas.setFont("Helvetica", 12)
    current_date = datetime.now().strftime("%Y-%m-%d")

    if employee:
        logo_path = employee.company.logo.path if employee.company and employee.company.logo else None


        if logo_path:
            logo_width = 80 
            logo_height = 80  #
            pdf_canvas.drawImage(logo_path, margin, y_position + 30, width=logo_width, height=logo_height)  # Adjust position
    
    
        pdf_canvas.setFont("Helvetica-Bold", 14)  
        y_position -= line_height
        pdf_canvas.drawString(margin, y_position, employee.company.name) if employee.company else None
        y_position -= line_height
        pdf_canvas.setFont("Helvetica", 10)
        if employee.company and employee.company.company_locations.exists():
            company_location = employee.company.company_locations.first()
            pdf_canvas.drawString(margin, y_position, company_location.address)
            y_position -= line_height
            pdf_canvas.drawString(margin, y_position, f"{company_location.phone} | {company_location.email}")

        y_position -= 60  # Extra spacing

        # Offer Letter Title
        pdf_canvas.setFont("Helvetica-Bold", 12)
        pdf_canvas.drawString(margin, y_position, f"Offer Letter for {candidate.full_name}")
        y_position -= 40
        pdf_canvas.drawString(margin, y_position, f"For the Position: {candidate.applied_job}")
        y_position -= 40
        pdf_canvas.drawString(margin, y_position, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        y_position -=40

        # Body
        pdf_canvas.setFont("Helvetica", 11)
        company_name = employee.company.name if employee.company else "Company Name Not Available"
        job_title = candidate.applied_job.title if candidate.applied_job else "Job Title Not Available"

        body_text = f"""
    Dear {candidate.full_name},    

    We are pleased to offer you the position of { job_title} at {company_name}.
    We are impressed with your qualifications and believe you will be a valuable addition to our team.

    We are offering you a competitive salary, and we look forward to your joining us on {candidate.joining_deadline}.

    Your key remuneration is as follows:
    - Basic Salary: {(candidate.applied_job.salary_structure.basic_salary):.2f}
    - House Allowance: {(candidate.applied_job.salary_structure.hra):.2f}
    - Medical Allowance: {(candidate.applied_job.salary_structure.medical_allowance):.2f}
    - Conveyance Allowance: {(candidate.applied_job.salary_structure.conveyance_allowance):.2f}
    - Festival Bonus: {(candidate.applied_job.salary_structure.festival_allowance):.2f}
    - Performance Bonus: {(candidate.applied_job.salary_structure.performance_bonus):.2f}
    - Provident Fund: {(candidate.applied_job.salary_structure.provident_fund):.2f}
    - Professional Tax: {(candidate.applied_job.salary_structure.professional_tax):.2f}
    - Income Tax: {(candidate.applied_job.salary_structure.income_tax):.2f}

    Please review the terms and conditions of your employment and feel free to reach out if you have any questions.

    Best regards,
    {employee.name}
    {employee.position}
    {company_name }
    """
        for line in body_text.strip().split("\n"):
            pdf_canvas.drawString(margin, y_position, line.strip())
            y_position -= line_height

            if y_position < 100:  # New page if necessary
                pdf_canvas.showPage()
                pdf_canvas.setFont("Helvetica", 11)
                y_position = 780

        pdf_canvas.showPage()
        pdf_canvas.save()
        buffer.seek(0)
        return buffer






@login_required
def preview_offer_letter(request, candidate_id): 
    selected_candidates = Candidate.objects.filter(interview_status='INTERVIEW-PASS')
    candidate = get_object_or_404(Candidate, id=candidate_id)
    employee = Employee.objects.filter(user_profile__user=request.user).first()
    
    if not employee:
        messages.error(request, 'Employee profile not found.')
        return redirect('recruitment:selected_candidate') 
    
    pdf_buffer = generate_offer_letter_pdf(candidate, employee)
    pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')

    return render(request, "customerportal/recruitment/offer_letter_preview.html", {
        "candidate": candidate,
        "pdf_preview": pdf_base64,
        "selected_candidates": selected_candidates
    })











from recruitment.models import CommonDocument,CandidateDocument
from core.forms import AddEmployeeForm
from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from django.core.mail import EmailMessage,send_mail


def candidate_joining(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)  
    # if not candidate.manager_confirmation_of_joining:
    #     messages.warning(request, "Hiring Manager has not approved the onboarding yet.")
    #     return redirect("customerportal:job_list_candidate_view")

    # if candidate.joining_deadline and candidate.joining_deadline < timezone.now().date():
    #     messages.warning(request, 'Your timing of joining has expired')
    #     return redirect("customerportal:job_list_candidate_view")

    if request.method == "POST":
        form = AddEmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)          
            employee.save()

            subject = f"Welcome to {candidate.applied_job.company} - Your Employment Details"
            message = render_to_string("recruitment/onboard_welcome_template.html", {"employee": employee})
            email = EmailMessage(
                subject,
                message,
                "hr@yourcompany.com",  
                [employee.email],  
            )
           
            common_documents = CommonDocument.objects.all()
            for doc in common_documents:
                email.attach(doc.name, doc.file.read(), doc.file.content_type)

            candidate_documents = CandidateDocument.objects.filter(candidate=candidate)
            for doc in candidate_documents:
                email.attach(doc.name, doc.file.read(), doc.file.content_type)

            email.send(fail_silently=False)         
                                
            candidate.hiring_status = True
            candidate.onboard_status = "onboard"
            candidate.save()
     
            if candidate.candidate:
                user = candidate.candidate
                job_seekers = Group.objects.get(name="Job_seekers")
                staff_group, _ = Group.objects.get_or_create(name="Staff")

                user.groups.remove(job_seekers)
                user.groups.add(staff_group)

            messages.success(request, f"{candidate.full_name} has officially joined the company.")
            return redirect("accounts:login")
    else:
       form = AddEmployeeForm(initial={
            "name": candidate.full_name,
            "email": candidate.email,  
            "salary_structure": candidate.applied_job.salary_structure,          
            "department": candidate.applied_job.department,
            "position": candidate.applied_job.position,  
            "location": candidate.applied_job.location,
            "joining_date": candidate.expected_joining_date,
            "company": candidate.applied_job.company,
            "gender": candidate.gender,
            'user_profile':candidate.candidate.user_profile,
           
        })
    return render(request, "customerportal/recruitment/candidate_joining.html", {"form": form, "candidate": candidate})
   


def search_applications(request):
    form = SearchApplicationForm(request.GET or None)  
    candidates = Candidate.objects.all()  

    if form.is_valid(): 
        query = form.cleaned_data.get('query')
        if query:   
            candidates = candidates.filter(
                full_name__icontains=query
            ) | candidates.filter(email__icontains=query)

    return render(request, 'customerportal/recruitment/search_applications.html', {
        'form': form,
        'candidates': candidates,
    })


