
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

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db import transaction
from clients.models import Client,SubscriptionPlan

from .forms import AssignPermissionsForm
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Permission
from django.apps import apps
from django.http import JsonResponse
from django.contrib.auth.models import User, Group
from .forms import UserGroupForm
from .forms import AssignPermissionsToGroupForm
from django.core.paginator import Paginator
from transport.models import Transport
from django.contrib.auth.models import Group
from tasks.models import Ticket,Task
from django_tenants.utils import schema_context


def home(request):
    return render(request,'accounts/home.html')



@login_required
def register_view(request):
    current_tenant = None
    if hasattr(connection, 'tenant'):
        current_tenant = connection.tenant.schema_name

    if request.method == 'POST':
        form = TenantUserRegistrationForm(request.POST, request.FILES, tenant=current_tenant)
        if form.is_valid():
            with transaction.atomic():    
                user = form.save(commit=False)
                user.email = form.cleaned_data['email']
                user.save()
                UserProfile.objects.create(
                    user=user,
                    tenant=Client.objects.filter(schema_name=current_tenant).first(),
                    profile_picture=form.cleaned_data.get('profile_picture'),
                )

            messages.success(request, "User registered successfully!")
            return redirect('accounts:login')
        else:
            messages.error(request, "There was an error with your registration.")
    else:
        form = TenantUserRegistrationForm(tenant=current_tenant)
    return render(request, 'accounts/registration/register.html', {'form': form})




def register_customer_support(request):
    current_tenant = None
    if hasattr(connection, 'tenant'):
        current_tenant = connection.tenant.schema_name

    if request.method == 'POST':
        form = TenantUserRegistrationForm(request.POST, request.FILES, tenant=current_tenant)
        if form.is_valid():
            with transaction.atomic():    
                user = form.save(commit=False) 
                user.email = form.cleaned_data['email']
                user.save() 

                customer_group, created = Group.objects.get_or_create(name='Customer')
                user.groups.add(customer_group)  

                UserProfile.objects.create(
                    user=user,
                    tenant=Client.objects.filter(schema_name=current_tenant).first(),
                    profile_picture=form.cleaned_data.get('profile_picture'),
                )

            messages.success(request, "User registered successfully!")
            return redirect('accounts:login')
        else:
            messages.error(request, "There was an error with your registration.")
    else:
        form = TenantUserRegistrationForm(tenant=current_tenant)

    return render(request, 'accounts/registration/register_customer_support.html', {'form': form})




def register_job_seeker(request):
    current_tenant = None
    if hasattr(connection, 'tenant'):
        current_tenant = connection.tenant.schema_name

    if request.method == 'POST':
        form = TenantUserRegistrationForm(request.POST, request.FILES, tenant=current_tenant)
        if form.is_valid():
            with transaction.atomic():    
                user = form.save(commit=False) 
                user.email = form.cleaned_data['email']
                user.save() 

                job_seekers, created = Group.objects.get_or_create(name='job_seekers')
                user.groups.add(job_seekers) 
                UserProfile.objects.create(
                    user=user,
                    tenant=Client.objects.filter(schema_name=current_tenant).first(),
                    profile_picture=form.cleaned_data.get('profile_picture'),
                )

            messages.success(request, "User registered successfully!")
            return redirect('accounts:login')
        else:
            messages.error(request, "There was an error with your registration.")
    else:
        form = TenantUserRegistrationForm(tenant=current_tenant)

    return render(request, 'accounts/registration/register_job_seeker.html', {'form': form})





@login_required
def update_profile_picture(request): 
    if not request.user.is_authenticated:
        return redirect('core:home') 

    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    profile_picture_url = user_profile.profile_picture.url if user_profile.profile_picture else None
    user_info = request.user.get_full_name() or request.user.username

    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            if request.user.groups.filter(name='Customer').exists():
                        return redirect('customerportal:create_ticket')  
            else:
                messages.success(request, "Login successful!")
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
            if current_tenant == tenant:
                user = authenticate(request, username=username, password=password)
            else:
                messages.warning(request,'Your not in correct tenant. Please login with our own tenant')
            if user:            
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('clients:tenant_expire_check')             
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid form")
    else:
        form = CustomLoginForm(initial={'tenant': current_tenant})    
    return render(request, 'accounts/registration/login.html', {'form': form})


def login_customer_support_view(request):
    current_tenant = None
    if hasattr(connection, 'tenant'):
        current_tenant = connection.tenant.schema_name 

    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            tenant = form.cleaned_data['tenant']  # The tenant schema entered by the user

            user = authenticate(request, username=username, password=password)
            if user is not None:             
                if hasattr(user, 'user_profile'):
                    user_tenant = user.user_profile.tenant
                    if user_tenant and user_tenant.schema_name == tenant:
                        login(request, user)
                        
                        # Redirect based on user group
                        if user.groups.filter(name='Customer').exists():
                            return redirect('customerportal:ticket_list') 
                        else:
                            messages.success(request, "Login successful!")
                            return redirect('clients:tenant_expire_check')  
                    else:
                        messages.error(request, "Invalid tenant. You are not allowed to log in to this tenant.")
                else:
                    messages.error(request, "User profile is missing. Contact admin for support.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm(initial={'tenant': current_tenant})    
    return render(request, 'accounts/registration/login_customer_support.html', {'form': form})



def login_job_seeker_view(request):
    current_tenant = None
    if hasattr(connection, 'tenant'):
        current_tenant = connection.tenant.schema_name 

    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            tenant = form.cleaned_data['tenant']  
            if current_tenant == tenant:
                user = authenticate(request, username=username, password=password)
            else:
                messages.warning(request,'Your not in correct tenant. Please login with our own tenant')
            if user:            
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('clients:tenant_expire_check')             
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid form")
    else:
        form = CustomLoginForm(initial={'tenant': current_tenant})    
    return render(request, 'accounts/registration/login_job_seeker.html', {'form': form})



def logged_out_view(request):
    plans = SubscriptionPlan.objects.all().order_by('duration')
    for plan in plans:
        plan.features_list = plan.features.split(',')
    is_customer = False
    if request.user.is_authenticated:        
        is_customer = request.user.groups.filter(name='Customer').exists()
       
    logout(request)

    if is_customer:
        return render(request, 'accounts/registration/logged_out_customer.html',{'plans':plans})
    return render(request, 'accounts/registration/logged_out.html',{'plans':plans})



def assign_model_permission_to_user(user, model_name, permission_codename): 
    try:
        app_label, model_label = model_name.split('.')
        model = apps.get_model(app_label, model_label)
        content_type = ContentType.objects.get_for_model(model)
        permission = Permission.objects.get(codename=permission_codename, content_type=content_type)

        user.user_permissions.add(permission)
        user.save()
        
        return f"Permission '{permission_codename}' successfully assigned to {user.username}."
    except Permission.DoesNotExist:
        return f"Permission '{permission_codename}' does not exist for the model '{model_name}'."
    except Exception as e:
        return f"An error occurred: {e}"



@login_required
def assign_permissions(request):
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to assign roles.")
        return redirect('core:home')

    if request.method == 'POST':
        form = AssignPermissionsForm(request.POST)
        if form.is_valid():
            try:
                user = form.cleaned_data['user']
                selected_permissions = form.cleaned_data['permissions']
                model_name = form.cleaned_data['model_name']   
                email = form.cleaned_data['email']             

                cleaned_model_name = model_name.strip("[]").strip("'\"")
                
                user = User.objects.get(email=email)
                
                for permission_codename in selected_permissions:
                    cleaned_codename = permission_codename.strip("[]").strip("'\"")                    

                    message = assign_model_permission_to_user(user, cleaned_model_name, cleaned_codename)
                    messages.success(request, message)
                
                return redirect('accounts:assign_permissions')
            except Permission.DoesNotExist:
                messages.error(request, f"Permission '{permission_codename}' does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
    else:
        form = AssignPermissionsForm()

    users = User.objects.all().order_by('-date_joined')
    paginator = Paginator(users,8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'accounts/assign_permission.html', {'form': form, 'users': users,'page_obj':page_obj})



@login_required
def assign_user_to_group(request):
    group_data = Group.objects.all()

    if request.method == 'POST':
        form = UserGroupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email'] 
            group = form.cleaned_data['group']
            new_group_name = form.cleaned_data['new_group_name']

            try:
                user = User.objects.get( email=email)
            except User.DoesNotExist:
                messages.error(request, f"User '{username}' does not exist.")
                return redirect('accounts:assign_user_to_group')

            if group:
                user.groups.add(group)
                messages.success(request, f"User '{email}' was added to the existing group '{group.name}'.")
            elif new_group_name:
                group, created = Group.objects.get_or_create(name=new_group_name)
                user.groups.add(group)
                if created:
                    messages.success(request, f"Group '{new_group_name}' was created and '{username}' was added to it.")
                else:
                    messages.success(request, f"User '{username}' was added to the existing group '{new_group_name}'.")
            
            user.save()
            return redirect('accounts:assign_user_to_group')
    else:
        form = UserGroupForm()
    return render(request, 'accounts/assign_user_to_group.html', {'form': form,'group_data':group_data})




def assign_permissions_to_group(request):
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to assign roles.")
        return redirect('core:home')

    group_name = None
    assigned_permissions = []
    group_data = Group.objects.all() 

    if request.method == 'POST':
        form = AssignPermissionsToGroupForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            model_name = form.cleaned_data['model_name']
            selected_permissions = form.cleaned_data['permissions']

            try:
                model_class = apps.get_model(*model_name.split('.'))
                content_type = ContentType.objects.get_for_model(model_class)

                for permission in selected_permissions:
                    if permission.content_type == content_type:
                        group.permissions.add(permission)

                group_name = group.name
                assigned_permissions = group.permissions.select_related('content_type').all() 
                messages.success(request, f"Permissions successfully assigned to the group '{group.name}'.")
                return redirect('accounts:assign_permissions_to_group')

            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
        else:
            print(form.errors)
    else:
        form = AssignPermissionsToGroupForm()

    groups_info = []
    for group in group_data:
        users_in_group = group.user_set.all() 
        permissions_in_group = group.permissions.select_related('content_type').all()  
        groups_info.append({
            'group': group,
            'users': users_in_group,
            'permissions': permissions_in_group
        })

    return render(
        request,
        'accounts/assign_permissions_to_group.html',
        {
            'form': form,
            'group_name': group_name,
            'assigned_permissions': assigned_permissions,
            'groups_info': groups_info,  # Pass the group data to the template
        }
    )



# for ajax
def get_permissions_for_model(request):
    model_name = request.GET.get('model_name', '')    
    try:
        app_label, model_name = model_name.split('.')
        model_class = apps.get_model(app_label, model_name)   
        content_type = ContentType.objects.get_for_model(model_class) 
        permissions = Permission.objects.filter(content_type=content_type)
        permission_data = [
            {'id': perm.id, 'name': perm.name, 'codename': perm.codename}
            for perm in permissions
        ]        
        return JsonResponse({'permissions': permission_data})    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)




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

        vehicle = Transport.objects.filter(
            Q(vehicle_registration_number__icontains=query)
        ).values('id', 'vehicle_registration_number')
        results.extend([
            {'id': data['id'], 'text': f"{data['vehicle_registration_number']}"}
            for data in vehicle
        ]) 

    return JsonResponse({'results': results})



@login_required
def search_all(request):
    query = request.GET.get('q')
   
    employees = Employee.objects.filter(
        Q(name__icontains=query) | 
        Q(employee_code__icontains=query) | 
        Q(email__icontains=query) | 
        Q(phone__icontains=query) | 
        Q(position__name__icontains=query) | 
        Q(department__name__icontains=query)
    )

    products = Product.objects.filter(
        Q(name__icontains=query)         
    )
    tickets = Ticket.objects.filter(
        Q(ticket_id__icontains=query)         
    )

    tasks = Task.objects.filter(
        Q(task_id__icontains=query)         
    )



    return render(request, 'accounts/search_results.html', {
        'employees': employees, 
        'products':products,
        'tickets':tickets,
        'tasks':tasks,
        'query': query,
        
    })
