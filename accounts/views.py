
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse,JsonResponse
from django.db.models import Q

from .forms import UserRegistrationForm,CustomLoginForm,CustomUserCreationForm,ProfilePictureForm
from.models import UserProfile

from inventory.models import TransferOrder,Warehouse
from product.models import Product,Category
from core.models import Employee
from purchase.models import PurchaseOrder,PurchaseRequestOrder
from logistics.models import PurchaseShipment,SaleShipment
from finance.models import PurchaseInvoice,SaleInvoice,PurchasePayment,SalePayment
from sales.models import SaleOrder,SaleRequestOrder
from manufacture.models import MaterialsRequestOrder
from operations.models import OperationsRequestOrder

from django.db import connection
from .forms import TenantUserRegistrationForm

def home(request):
    return render(request,'accounts/home.html')



def register_view(request):
    current_tenant = None
    if hasattr(connection, 'tenant'):
        current_tenant = connection.tenant.schema_name

    if request.method == 'POST':
        form = TenantUserRegistrationForm(request.POST, request.FILES,tenant=current_tenant)
        if form.is_valid():
            form.save()
            messages.success(request, "User registered successfully!")
            return redirect('accounts:login')  
        else:
            messages.error(request, "There was an error with your registration.")
    else:
        form = TenantUserRegistrationForm(tenant=current_tenant)
    return render(request, 'accounts/registration/register.html', {'form': form})




@login_required
def update_profile_picture(request):
    print(request.user)
    if not request.user.is_authenticated:
        return redirect('core:home') 

    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    profile_picture_url = user_profile.profile_picture.url if user_profile.profile_picture else None
    user_info = request.user.get_full_name() or request.user.username

    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('core:home')
    else:
        form = ProfilePictureForm(instance=user_profile)

    return render(
        request, 
        'accounts/change_profile_picture.html', 
        {'form': form, 'user_info': user_info, 'profile_picture_url': profile_picture_url}
    )




def login_view(request):
    current_tenant = None
    if hasattr(connection, 'tenant'):
        current_tenant = connection.tenant.schema_name 

    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            tenant = form.cleaned_data['tenant']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                if hasattr(user, 'user_profile') and user.user_profile.tenant.schema_name == tenant:
                    login(request, user)
                    messages.success(request, "Login successful!")
                    return redirect('clients:tenant_expire_check')  # Redirect to the home page after login
                else:
                    messages.error(request, "Invalid tenant. You are not allowed to log in to this tenant.")                                                   
            else:
                messages.error(request, "Invalid username or password.")
    else:
         form = CustomLoginForm(initial={'tenant': current_tenant})
    return render(request, 'accounts/registration/login.html', {'form': form})



def logged_out_view(request):
    return render(request, 'accounts/registration/logged_out.html')


def password_reset_done(request):
    return render(request, 'accounts/registration/password_reset_done.html')




def common_search(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(product_id__icontains=query)
        ).values('id', 'name', 'product_id')
        results.extend([
            {'id': prod['id'], 'text': f"{prod['name']} ({prod['product_id']})"}
            for prod in products
        ])

        categories = Category.objects.filter(
            Q(name__icontains=query) | Q(category_id__icontains=query)
        ).values('id', 'name', 'category_id')
        results.extend([
            {'id': prod['id'], 'text': f"{prod['name']} ({prod['category_id']})"}
            for prod in categories
        ])

        employees = Employee.objects.filter(
            Q(name__icontains=query) | Q(employee_code__icontains=query)
        ).values('id', 'name', 'employee_code')
        results.extend([
            {'id': emp['id'], 'text': f"{emp['name']} ({emp['employee_code']})"}
            for emp in employees
        ])   

        purchase_orders = PurchaseOrder.objects.filter(
            Q(order_id__icontains=query)
        ).values('id', 'order_id')
        results.extend([
            {'id': data['id'], 'text': f"{data['order_id']}"}
            for data in purchase_orders
        ])   

        purchase_request_orders = PurchaseRequestOrder.objects.filter(
            Q(order_id__icontains=query)
        ).values('id', 'order_id')
        results.extend([
            {'id': data['id'], 'text': f"{data['order_id']}"}
            for data in purchase_request_orders
        ])   

        
        purchase_shipment_orders = PurchaseShipment.objects.filter(
            Q(shipment_id__icontains=query)
        ).values('id', 'shipment_id')
        results.extend([
            {'id': data['id'], 'text': f"{data['shipment_id']}"}
            for data in purchase_shipment_orders
        ])       


        purchase_invoice_numbers = PurchaseInvoice.objects.filter(
            Q(invoice_number__icontains=query)
        ).values('id', 'invoice_number')
        results.extend([
            {'id': data['id'], 'text': f"{data['invoice_number']}"}
            for data in purchase_invoice_numbers
        ])  


        sale_orders = SaleOrder.objects.filter(
            Q(order_id__icontains=query)
        ).values('id', 'order_id')
        results.extend([
            {'id': data['id'], 'text': f"{data['order_id']}"}
            for data in sale_orders
        ])   

        sale_request_orders = SaleRequestOrder.objects.filter(
            Q(order_id__icontains=query)
        ).values('id', 'order_id')
        results.extend([
            {'id': data['id'], 'text': f"{data['order_id']}"}
            for data in sale_request_orders
        ])        


        sale_shipment_orders = SaleShipment.objects.filter(
            Q(shipment_id__icontains=query)
        ).values('id', 'shipment_id')
        results.extend([
            {'id': data['id'], 'text': f"{data['shipment_id']}"}
            for data in sale_shipment_orders
        ])       


        sale_invoice_numbers = SaleInvoice.objects.filter(
            Q(invoice_number__icontains=query)
        ).values('id', 'invoice_number')
        results.extend([
            {'id': data['id'], 'text': f"{data['invoice_number']}"}
            for data in sale_invoice_numbers
        ])   

        transfer_id = TransferOrder.objects.filter(
            Q(order_number__icontains=query)
        ).values('id', 'order_number')
        results.extend([
            {'id': data['id'], 'text': f"{data['order_number']}"}
            for data in transfer_id
        ]) 
    
        materials_orders = MaterialsRequestOrder.objects.filter(
            Q(order_id__icontains=query)
        ).values('id', 'order_id')
        results.extend([
            {'id': data['id'], 'text': f"{data['order_id']}"}
            for data in materials_orders
        ]) 

        operations_orders = OperationsRequestOrder.objects.filter(
            Q(order_id__icontains=query)
        ).values('id', 'order_id')
        results.extend([
            {'id': data['id'], 'text': f"{data['order_id']}"}
            for data in operations_orders
        ]) 

    return JsonResponse({'results': results})


