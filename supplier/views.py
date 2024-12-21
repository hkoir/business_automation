from django.shortcuts import render,redirect,get_object_or_404
from.models import SupplierPerformance
from django.core.paginator import PageNotAnInteger,Paginator,EmptyPage,Page
from django.contrib import messages
from.forms import SupplierPerformanceForm,AddLocationForm,AddSupplierForm
from.models import Supplier,SupplierPerformance,Location
from django.contrib.auth.decorators import login_required,permission_required


@login_required
def supplier_dashboard(request):
    return render(request,'supplier/supplier_dashboard.html')



@login_required
def create_supplier(request):
    suppliers = Supplier.objects.all().order_by('-created_at')
    form = AddSupplierForm(request.POST or None)

    if request.method == 'POST':
        if 'supplier_submit' in request.POST:
            if form.is_valid():
                supplier = form.save(commit=False)  
                supplier.user = request.user
                supplier.save()
                messages.success(request, "Supplier added successfully")
                return redirect('supplier:create_supplier')
            else:
                messages.error(request, "Form is invalid. Please check the details and try again.")

        elif 'action' in request.POST:
            action = request.POST['action']
            supplier_id = request.POST.get('supplier_id')

            if supplier_id and supplier_id.isdigit():
                supplier_id = int(supplier_id)
                
                if action == 'update':
                    supplier_obj = get_object_or_404(Supplier, id=supplier_id)
                    form = AddSupplierForm(request.POST, instance=supplier_obj) 
                    if form.is_valid():
                        form.save()
                        messages.success(request, "Supplier updated successfully")
                        return redirect('supplier:create_supplier')
                    else:
                        messages.error(request, "Form is invalid. Please check the details.")
                    
                elif action == 'delete':
                    supplier_obj = get_object_or_404(Supplier, id=supplier_id)
                    supplier_obj.delete()
                    messages.success(request, "Supplier deleted successfully")
                    return redirect('supplier:create_supplier')
            else:
                messages.error(request, "Supplier ID is missing or invalid.")

    paginator = Paginator(suppliers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'supplier/create_supplier.html', {'form': form, 'page_obj': page_obj})


@login_required
def create_location(request):
    locations = Location.objects.all().order_by('-created_at')
    form = AddLocationForm(request.POST or None)
    if request.method == 'POST':
        if 'location_submit' in request.POST:
            if form.is_valid():
                form_instance = form.save(commit=False)
                form_instance.user = request.user
                form_instance.save()
                messages.success(request, "Location added successfully")
                return redirect('supplier:create_location')
            else:
                messages.error(request, "Form is invalid. Please check the details and try again.")                       
    paginator = Paginator(locations, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'supplier/create_location.html', {'form': form, 'page_obj': page_obj})

@login_required
def update_location(request, location_id):
    locations = Location.objects.all().order_by('-created_at')
    location_instance = get_object_or_404(Location, id=location_id)
    if request.method == 'POST':
        form = AddLocationForm(request.POST, instance=location_instance)
        if form.is_valid():
            form_instance = form.save(commit=False)
            form_instance.user = request.user
            form_instance.save()
            messages.success(request, 'Location updated successfully!')
            return redirect('supplier:create_location')
    else:
        form = AddLocationForm(instance=location_instance)
    paginator = Paginator(locations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'supplier/update_location.html', {
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
        return redirect('supplier:create_location')
    return render(request, 'supplier/confirm_delete.html', {'location': location_obj})



@login_required
def supplier_performance_list(request):
    performances = SupplierPerformance.objects.all().order_by('-created_at')
    paginator = Paginator(performances, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'supplier/supplier_performance_list.html', {'page_obj': page_obj})


@login_required
def add_or_update_performance(request, performance_id=None):
    if performance_id:
        performance = get_object_or_404(SupplierPerformance, id=performance_id)
        message_text = "Performance updated successfully!"
    else:
        performance = None
        message_text = "Performance added successfully!"
        
    form = SupplierPerformanceForm(request.POST or None, instance=performance)

    if request.method == 'POST':
        if form.is_valid():
            form_instance = form.save(commit=False)
            form_instance.user = request.user
            form_instance.save()           
            messages.success(request, message_text)
            return redirect('supplier:supplier_performance_list')

    return render(request, 'supplier/create_or_update_performance.html', {'form': form, 'performance': performance})


