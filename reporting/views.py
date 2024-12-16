
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Sum
import json,csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from num2words import num2words
import os
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import now, timedelta
from datetime import timedelta
from django.http import HttpResponse
from django.contrib import messages

from django.core.paginator import Paginator
from django.db.models.signals import post_save, post_delete

from.forms import SummaryReportChartForm
from core.models import Employee
from product.models import Product
from inventory.models import Inventory,TransferOrder,Warehouse,InventoryTransaction
from purchase.models import PurchaseOrder
from repairreturn.models import Replacement
from sales.models import SaleOrder
from.models import Notification

from utils import mark_notification_as_read,calculate_stock_value2

from django.core.mail import send_mail
from core.forms import CommonFilterForm



def report_dashboard(request):
    return render(request, 'report/report_dashboard.html')



def notification_list(request):
    notifications = Notification.objects.all().order_by('-created_at')
    unread_notifications = notifications.filter(user=request.user, is_read=False)
    paginator = Paginator(notifications, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'report/notification_list.html',{'notifications':notifications,'page_obj':page_obj,'unread_notifications':unread_notifications})


def mark_notification_read_view(request, notification_id):
    mark_notification_as_read(notification_id)
    return redirect('reporting:notification_list')




def product_list(request):
    product = None
    products = Product.objects.all().order_by('-created_at')
    form = CommonFilterForm(request.GET or None)  
    if form.is_valid():
        product = form.cleaned_data.get('product_name')
        if product:
            products = products.filter(name__icontains=product.name)  
    
    paginator = Paginator(products, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form=CommonFilterForm()

    return render(request, 'report/product_list.html', {
        'products': products,
        'page_obj': page_obj,
        'product': product,
        'form': form,
    })




def product_report(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    warehouses = Warehouse.objects.all()
    grand_total_stock =0

    warehouse_data = []
    for warehouse in warehouses:
        stock_data = calculate_stock_value2(product=product, warehouse=warehouse)

        stock_value = stock_data['total_available'] * float(product.unit_price)
        grand_total_stock += stock_value

      
        warehouse_entry = {
            'warehouse_name': warehouse.name,
            'warehouse_id': warehouse.id,
            'total_available': stock_data['total_available'],
            'total_purchased': stock_data['total_purchase'],
            'total_manufacture_in': stock_data['total_manufacture_in'],
            'total_manufacture_out': stock_data['total_manufacture_out'],
            'total_existing_in': stock_data['total_existing_in'],

            'total_sold': stock_data['total_sold'],
            'total_refund_out': stock_data['total_replacement_out'],
            'total_refund_in': stock_data['total_replacement_in'],
            'total_incoming': stock_data['total_transfer_in'],
            'total_outgoing': stock_data['total_transfer_out'],
            'total_scrapped_in': stock_data['total_scrapped_in'],
            'total_scrapped_out': stock_data['total_scrapped_out'],
            'total_operations_out': stock_data['total_operations_out'],

            'total_stock_value': stock_data['total_available'] * float(product.unit_price),
            'total_stock': stock_data['total_stock'],
             
        }
        warehouse_data.append(warehouse_entry)


    total_data = calculate_stock_value2(product=product)

    warehouse_data_json = json.dumps(warehouse_data)

    return render(request, 'report/product_report.html', {
        'product': product,
        'warehouse_data': warehouse_data,
        'total_data': total_data,
        'warehouse_data_json': warehouse_data_json,
        'grand_total_stock':grand_total_stock
    })




def warehouse_report(request):
    warehouses = Warehouse.objects.all()
    warehouse_data = []
    warehouse_json = None
    days = None
    start_date = None
    end_date = None
    form = SummaryReportChartForm(request.GET or {'days': 60}) 
    
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days') 
        warehouse_name = form.cleaned_data.get('warehouse_name') 
        product_name = form.cleaned_data.get('product_name') 

        if start_date and end_date:         
            start_date = timezone.make_aware(start_date) if timezone.is_naive(start_date) else start_date
            end_date = timezone.make_aware(end_date) if timezone.is_naive(end_date) else end_date
            warehouses = warehouses.filter(created_at__range=(start_date, end_date))
        elif days:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            warehouses = warehouses.filter(created_at__range=(start_date, end_date)) 

        if warehouse_name:
            warehouses = warehouses.filter(name=warehouse_name)
        
        for warehouse in warehouses:
            products_in_warehouse = Inventory.objects.filter(warehouse=warehouse)
            
            if product_name:
                products_in_warehouse = products_in_warehouse.filter(product__name__icontains=product_name)
           
            products_in_warehouse = products_in_warehouse.values('product__id', 'product__name').annotate(
                total_available=Sum('quantity')
            )
           
            product_details = []
            for product in products_in_warehouse:
                product_id = product['product__id']
                product_name = product['product__name']
                
                total_purchased = PurchaseOrder.objects.filter(purchase_order_item__product_id=product_id, purchase_transactions__warehouse=warehouse).aggregate(total=Sum('purchase_order_item__quantity'))['total'] or 0
                total_sold = SaleOrder.objects.filter(sale_order__product_id=product_id, sale_order__warehouse=warehouse).aggregate(total=Sum('sale_order__quantity'))['total'] or 0
                total_incoming = TransferOrder.objects.filter(transfers__product_id=product_id, transfers__target_warehouse=warehouse).aggregate(total=Sum('transfers__quantity'))['total'] or 0
                total_outgoing = TransferOrder.objects.filter(transfers__product_id=product_id, transfers__source_warehouse=warehouse).aggregate(total=Sum('transfers__quantity'))['total'] or 0                                 
                          
                total_replacement = Replacement.objects.filter(faulty_product__product_id=product_id, warehouse=warehouse).aggregate(total=Sum('quantity'))['total'] or 0
              
                

                product_details.append({
                    'product_name': product_name,
                    'total_available': product['total_available'],
                    'total_purchased': total_purchased,
                    'total_sold': total_sold,
                    'total_replacement': total_replacement,
                    'total_incoming': total_incoming,
                    'total_outgoing': total_outgoing,
                   
                })
            
            warehouse_data.append({
                'warehouse_name': warehouse.name,
                'products': product_details
            })

        warehouse_json = json.dumps(warehouse_data)  
            
    paginator = Paginator(warehouse_data, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form = SummaryReportChartForm() 
    return render(request, 'report/warehouse_report.html', {
        'warehouse_data': warehouse_data,
        'warehouse_data': page_obj, 
        'page_obj': page_obj,
        'warehouse_json': warehouse_json,
        'form': form,
        'days': days,
        'start_date': start_date,
        'end_date': end_date
    })




def warehouse_report_nofilter(request):
    warehouses = Warehouse.objects.all()
    warehouse_data = []
    warehouse_json = None  
        
    for warehouse in warehouses:
        products_in_warehouse = Inventory.objects.filter(warehouse=warehouse)      
        products_in_warehouse = products_in_warehouse.values('product__id', 'product__product_name').annotate(
            total_available=Sum('quantity')
        )
        
        product_details = []
        for product in products_in_warehouse:
            product_id = product['product__id']
            product_name = product['product__product_name']
            
            total_purchased = PurchaseOrder.objects.filter(product_id=product_id, warehouse=warehouse).aggregate(total=Sum('quantity'))['total'] or 0
            total_sold = SaleOrder.objects.filter(product_id=product_id, warehouse=warehouse).aggregate(total=Sum('quantity'))['total'] or 0
            total_incoming = TransferOrder.objects.filter(product_id=product_id, target_warehouse=warehouse).aggregate(total=Sum('quantity'))['total'] or 0
            total_outgoing = TransferOrder.objects.filter(product_id=product_id, source_warehouse=warehouse).aggregate(total=Sum('quantity'))['total'] or 0
            
            product_details.append({
                'product_name': product_name,
                'total_available': product['total_available'],
                'total_purchased': total_purchased,
                'total_sold': total_sold,
                'total_incoming': total_incoming,
                'total_outgoing': total_outgoing
            })
        
        warehouse_data.append({
            'warehouse_name': warehouse.warehouse_name,
            'products': product_details
        })

    warehouse_json = json.dumps(warehouse_data)

    paginator = Paginator(warehouse_data, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form = SummaryReportChartForm() 
    return render(request, 'report/warehouse_report.html', {
        'warehouse_data': warehouse_data,
        'warehouse_data': page_obj, 
        'page_obj': page_obj,
        'warehouse_json': warehouse_json,
        'form': form,

    })


def sale_order_detail(request, sale_order_id):
    sale_order = get_object_or_404(SaleOrder, id=sale_order_id)
    sold_products = SaleOrder.objects.filter(sale_order=sale_order)
    return render(request, 'invmanagement/purchase/purchase_order_details.html', {
        'sale_order': sale_order,
        'psold_products': sold_products,
    })



def download_sale_delivery_order_csv(request, order_id):
    sale_order = get_object_or_404(SaleOrder, id=order_id)    

    if 'download' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="delivery_order_{sale_order.order_id}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Order Number', 'Date', 'customer', 'Product','category', 'Quantity','Unit Price','toatl_price'])

        for sale in sale_order.sale_order.all():
            writer.writerow([
                sale_order.order_id,
                sale_order.order_date,
                 sale_order.customer.name,
                sale.product.name,
                sale.product.category,
                sale.quantity,             
                sale.product.unit_price,
                sale.total_price
            ])
        
        return response
    
    return render(request, 'report/download_sale_delivery_order_csv.html', {'sale_order': sale_order})




def generate_sale_challan(request, order_id):
    logo_path2 = os.path.join(settings.MEDIA_ROOT, 'profile_pictures', '5.jpg')  # Alternate option for image
    sale_order = get_object_or_404(SaleOrder, id=order_id)

    if 'download' in request.GET:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="challan_{sale_order.order_id}.pdf"'
       
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4

        # Header Information
        p.setFont("Helvetica-Bold", 16)
        p.drawString(140, height - 80, f"Challan/Invoice for Order Number: {sale_order.order_id}")
        p.drawString(140, height - 90, f".......................................................................................")
               
        # Logo
        logo_path = 'D:/SCM/dscm/media/logo.png'  
        
        logo_width = 60 
        logo_height = 60  
        p.drawImage(logo_path, 50, height - 110, width=logo_width, height=logo_height)

        # Customer Info
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 150, f"Order Date: {sale_order.order_date}")
        p.drawString(50, height - 170, f"Customer: {sale_order.customer.name}")
        p.drawString(260, height - 170, f"Phone: {sale_order.customer.phone}")
        p.drawString(50, height - 190, f"Address: {sale_order.customer.website}")

        # Table Headers
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, height - 250, "Product")
        p.drawString(200, height - 250, "Quantity")
        p.drawString(280, height - 250, "Product Type")
        p.drawString(380, height - 250, "Unit Price")
        p.drawString(480, height - 250, "Total Price")

        # Product Lines
        y = height - 280
        p.setFont("Helvetica", 12)
        grand_total = 0  # Initialize grand total

        for sale in sale_order.sale_order.all():
            p.drawString(50, y, sale.product.name)
            p.drawString(225, y, str(sale.quantity))
            p.drawString(290, y, sale.product.product_type if sale.product.product_type else 'N/A')
            p.drawString(390, y, f"{sale.product.unit_price:,.2f}" if sale.product.unit_price else 'N/A')
            p.drawString(480, y, f"{sale.total_price:,.2f}" if sale.total_price else 'N/A')


            grand_total += sale.total_price if sale.total_price else 0
            y -= 20

        p.setFont("Helvetica-Bold", 12)
        p.drawString(380, y - 20, "Grand Total:")
        p.drawString(480, y - 20, f"{grand_total:,.2f}")

        grand_total_words = num2words(grand_total, to='currency', lang='en').replace("euro", "Taka").replace("cents", "paisa").capitalize()

        p.setFont("Helvetica", 14)
        p.drawString(50, y - 40, f"Amount in words: {grand_total_words}")        
   
        cfo_employee = Employee.objects.filter(position='CFO').first()
        if cfo_employee:
            p.drawString(50,height - 660, f"Autorized Signature________________")  
            p.drawString(50, height - 680, f"Name:{cfo_employee.name}")  
            p.drawString(50,height - 700, f"Designation:{cfo_employee.position}")  
        else:
            p.drawString(50,height - 660, f"Autorized Signature________________")  
            p.drawString(50, height - 680, f"Name:........") 
            p.drawString(50, height - 700, f"Designation:.....")  
            p.setFont("Helvetica-Bold", 10)
            p.setFillColor('green')
            p.drawString(50,height - 730, f"(Signature is not mandatory due to computerized authorization)")
            
            p.setFont("Helvetica", 10)    
            p.setFillColor('black')       
            p.drawString(50,height - 780, f" Company's address: Block-D, House-123, Road# W2, Eastern Housing 2nd phase,Pallabi,Mirpur")
            p.drawString(50,height - 800, f" Dhaka North, Dhaka-1216, Phone: 01743800705, email:mymeplustech@gmail.com, web:www.mymeplus.com")        

        p.showPage()
        p.save()
        return response
    return render(request, 'report/generate_sale_challan_pdf.html', {'sale_order': sale_order})



def download_purchase_delivery_order_csv(request, order_id):
    purchase_order = get_object_or_404(PurchaseOrder, id=order_id)    

    if 'download' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="delivery_order_{purchase_order.purchase_order_id}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Order Number', 'Date', 'Product', 'Quantity', 'Product Type', 'Unit Price'])

        for purchase in purchase_order.purchases_order.all():
            writer.writerow([
                purchase_order.purchase_order_id,
                purchase_order.order_date,
                purchase.product.product_name,
                purchase.quantity,
                purchase.product.product_type,
                purchase.product.unit_price
            ])
        
        return response
    
    return render(request, 'report/download_purchase_delivery_order_csv.html', {'purchase_order': purchase_order})



def generate_purchase_challan(request, order_id): 
    purchase_order = get_object_or_404(PurchaseOrder, id=order_id)
    if 'download' in request.GET:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="challan_{purchase_order.purchase_order_id}.pdf"'
       
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4

        p.setFont("Helvetica-Bold", 16)
        p.drawString(150, height - 80, f"Challan/Invoice for Order: {purchase_order.purchase_order_id}")

        p.setFont("Helvetica", 12)
        p.drawString(50, height - 120, f"Order Date: {purchase_order.order_date}")
        p.drawString(50, height - 140, f"Customer: {purchase_order.supplier.supplier_name}")
        p.drawString(50, height - 160, f"Address: {purchase_order.supplier.address}")

        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, height - 230, "Product")
        p.drawString(250, height - 230, "Quantity")
        p.drawString(350, height - 230, "product Type")
        p.drawString(450, height - 230, "Unit price")

        y = height - 260
        p.setFont("Helvetica", 12)
        for purchase in purchase_order.purchases_order.all():
            p.drawString(50, y, purchase.product.product_name)
            p.drawString(250, y, str(purchase.quantity))
            p.drawString(350, y, purchase.product.product_type if purchase.product.product_type else 'N/A')
            p.drawString(450, y, str(purchase.product.unit_price) if purchase.product.unit_price else 'N/A')
            y -= 20
   

        cfo_employee = Employee.objects.filter(position='CFO').first()
        if cfo_employee:
            p.drawString(50,height - 700, f"Autorized Signature________________")  
            p.drawString(50, height - 720, f"Name:{cfo_employee.name}")  
            p.drawString(50,height - 740, f"Designation:{cfo_employee.position}")  
        else:
            p.drawString(50,height - 700, f"Autorized Signature________________")  
            p.drawString(50, height - 720, f"Name:........") 
            p.drawString(50, height - 740, f"Designation:.....")  
            p.setFont("Helvetica-Bold", 10)
            p.setFillColor('green')
            p.drawString(50,height - 780, f"Signature is not mandatory due to computerized authorization")  

        p.showPage()
        p.save()

        return response
  
    return render(request, 'report/generate_purchase_challan_pdf.html', {'purchase_order': purchase_order})




################## Reorder level and lead time notifications ###############################


def send_test_email():
    subject = "Test Email from Django"
    message = "This is a test email sent from the Django project."
    from_email = settings.EMAIL_HOST_USER  
    recipient_list = [settings.ADMIN_EMAIL] 

    try:
        send_mail(subject, message, from_email, recipient_list)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def calculate_average_usage(product, days=30):
    start_date = now() - timedelta(days=days)
    usage = InventoryTransaction.objects.filter(
        product=product,
        transaction_type='OUTBOUND',
        created_at__gte=start_date
    ).aggregate(total_usage=Sum('quantity'))['total_usage'] or 0

    return usage / days if usage else 0

def send_lead_time_alert(alerts):
    subject = "Lead Time Stock Alert"
    message = "The following products are at risk of stockout based on lead time and usage:\n\n"

    for alert in alerts:
        message += (
            f"Product: {alert['product']}\n"
            f"Warehouse: {alert['warehouse']}\n"
            f"Current Stock: {alert['current_stock']}\n"
            f"Required Stock (for {alert['lead_time']} days): {alert['required_stock']}\n"
            f"Average Daily Usage: {alert['average_usage']}\n\n"
        )
    send_mail(subject, message, 'noreply@yourcompany.com', ['admin@yourcompany.com'])

def send_warehouse_low_stock_alert(warehouse_wise_low_stock):
    subject = "Low Stock Alert (Warehouse-Wise)"
    message = "The following products have low stock in specific warehouses:\n\n"
    for item in warehouse_wise_low_stock:
        message += (
            f"Product: {item.product.name}\n"
            f"Warehouse: {item.warehouse.name if item.warehouse else 'N/A'}\n"
            f"Current Stock: {item.quantity}\n"
            f"Reorder Level: {item.product.reorder_level}\n\n"
        )
    send_mail(subject, message, 'noreply@yourcompany.com', ['admin@yourcompany.com'])

def send_total_low_stock_alert(low_stock_products):
    subject = "Low Stock Alert (Total)"
    message = "The following products have low total stock (across all warehouses):\n\n"
    for product in low_stock_products:
        message += (
            f"Product: {product['product_name']}\n"
            f"Total Stock: {product['total_quantity']}\n"
            f"Reorder Level: {product['reorder_level']}\n\n"
        )
    send_mail(subject, message, 'noreply@yourcompany.com', ['admin@yourcompany.com'])



def monitor_inventory_status(request):
    low_stock_alerts = []
    warehouse_wise_low_stock = []
    low_stock_products = []
    
    for product in Product.objects.all():
        average_usage = calculate_average_usage(product)
        required_stock = average_usage * product.lead_time
        warehouse_stocks = Inventory.objects.filter(product=product)

        for stock in warehouse_stocks:
            warehouse_reorder_level = stock.warehouse.reorder_level if stock.warehouse else product.reorder_level
            if stock.quantity < required_stock:
                low_stock_alerts.append({
                    'product': product.name,
                    'warehouse': stock.warehouse.name if stock.warehouse else 'N/A',
                    'current_stock': stock.quantity,
                    'required_stock': required_stock,
                    'average_usage': average_usage,
                    'lead_time': product.lead_time,
                })
            if stock.quantity <= warehouse_reorder_level:
                warehouse_wise_low_stock.append({
                    'product': product.name,
                    'warehouse': stock.warehouse.name if stock.warehouse else 'N/A',
                    'current_stock': stock.quantity,
                    'reorder_level': warehouse_reorder_level,
                })

        total_stock = warehouse_stocks.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        if total_stock < required_stock:
            low_stock_alerts.append({
                'product': product.name,
                'warehouse': 'All Warehouses',
                'current_stock': total_stock,
                'required_stock': required_stock,
                'average_usage': average_usage,
                'lead_time': product.lead_time,
            })
        if total_stock <= product.reorder_level:
            low_stock_products.append({
                'product': product.name,
                'warehouse': 'All Warehouses',
                'current_stock': total_stock,
                'reorder_level': product.reorder_level,
            })

    context = {
        'low_stock_alerts': low_stock_alerts,
        'warehouse_wise_low_stock': warehouse_wise_low_stock,
        'low_stock_products': low_stock_products,
    }
   
    # inventory_update_signal.send(
    #     sender=monitor_inventory_status,
    #     user=request.user, 
    #     message="This is a custom notification."
    #     )
    return render(request, 'report/monitor_inventory_status.html', context)




