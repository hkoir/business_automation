from django.shortcuts import render,redirect,get_object_or_404
from.forms import AddCustomerForm,AddLocationForm,UpdateLocationForm
from.models import Customer,Location
from django.core.paginator import Paginator
from django.contrib import messages

from .models import CustomerPerformance
from .forms import CustomerPerformanceForm 
from django.contrib.auth.decorators import login_required,permission_required


@login_required
def customer_dashboard(request):
    return render(request,'customer/customer_dashboard.html')


@login_required
def create_customer(request):
    customers =Customer.objects.all().order_by('-created_at')
    form = AddCustomerForm(request.POST or None)

    if request.method == 'POST':
        if 'customer_submit' in request.POST:
            if form.is_valid():
                customer = form.save(commit=False)  
                customer.user = request.user
                customer.save()
                messages.success(request, "Customer added successfully")
                return redirect('customer:create_customer')
            else:
                messages.error(request, "Form is invalid. Please check the details and try again.")

        elif 'action' in request.POST:
            action = request.POST['action']
            customer_id = int(request.POST.get('customer_id', 0))
            
            if action == 'update':
                customer_obj = get_object_or_404(Customer, id=customer_id)
                form = AddCustomerForm(request.POST, instance=customer_obj) 
                if form.is_valid():
                    form_intance=form.save(commit=False)
                    form_intance.user = request.user
                    form_intance.save()
                    messages.success(request, "Customer updated successfully")
                    return redirect('customer:create_customer')
                else:
                    messages.error(request, "Form is invalid. Please check the details.")
                form = AddCustomerForm(request.POST, instance=customer_obj)
                    
            elif action == 'delete':
                customer_obj = get_object_or_404(Customer, id=customer_id)
                customer_obj.delete()
                messages.success(request, "Customer deleted successfully")
                return redirect('customer:create_customer')    

    paginator = Paginator(customers, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'customer/create_customer.html', {'form': form, 'page_obj': page_obj})



@login_required
def create_location(request):
    locations = Location.objects.all().order_by('-created_at')
    form = AddLocationForm(request.POST or None)
    if request.method == 'POST':
        if 'location_submit' in request.POST:
            if form.is_valid():
                form_intance=form.save(commit=False)
                form_intance.user = request.user
                form_intance.save()
                messages.success(request, "Location added successfully")
                return redirect('customer:create_location')
            else:
                messages.error(request, "Form is invalid. Please check the details and try again.")                       
    paginator = Paginator(locations, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'customer/create_location.html', {'form': form, 'page_obj': page_obj})



@login_required
def update_location(request, location_id):
    locations = Location.objects.all().order_by('-created_at')
    location_instance = get_object_or_404(Location, id=location_id)
    if request.method == 'POST':
        form = AddLocationForm(request.POST, instance=location_instance)
        if form.is_valid():
            form_intance=form.save(commit=False)
            form_intance.user = request.user
            form_intance.save()
            messages.success(request, 'Location updated successfully!')
            return redirect('customer:create_location')
    else:
        form = AddLocationForm(instance=location_instance)
    paginator = Paginator(locations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'customer/update_location.html', {
        'form': form,
        'page_obj': page_obj,
        'location_instance': location_instance,
        'locations':locations
    })



@login_required
def delete_location(request, location_id):
    location_obj = get_object_or_404(Location, id=location_id)    
    if request.method == 'POST':
        location_obj.delete()
        messages.success(request, "Location deleted successfully")
        return redirect('customer:create_location')
    return render(request, 'customer/confirm_delete.html', {'location': location_obj})



@login_required
def customer_performance_list(request):
    performances = CustomerPerformance.objects.all().order_by('-created_at')
    paginator = Paginator(performances, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'customer/customer_performance_list.html', {'page_obj': page_obj})


@login_required
def add_or_update_performance(request, performance_id=None):
    if performance_id:
        performance = get_object_or_404(CustomerPerformance, id=performance_id)
        message_text = "Customer performance updated successfully!"
    else:
        performance = None
        message_text = "Customer performance added successfully!"
        
    form = CustomerPerformanceForm(request.POST or None, instance=performance)

    if request.method == 'POST':
        if form.is_valid():
            form_instance=form.save(commit=False)
            form_instance.user=request.user
            form_instance.save()
            messages.success(request, message_text)
            return redirect('customer:customer_performance_list')

    return render(request, 'customer/create_or_update_performance.html', {'form': form, 'performance': performance})


