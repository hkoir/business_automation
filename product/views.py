from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from.forms import AddCategoryForm,AddProductForm

from.models import Category,Product
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db import ProgrammingError

def product_dashboard(request):
    return render(request,'product/product_dashboard.html')

def manage_category(request, id=None):
    try:
        if request.method == 'POST' and 'delete_id' in request.POST:
            instance = get_object_or_404(Category, id=request.POST.get('delete_id'))
            instance.delete()
            messages.success(request, "Deleted successfully")
            return redirect('product:create_category')

        instance = get_object_or_404(Category, id=id) if id else None
        message_text = "updated successfully!" if id else "added successfully!"
        form = AddCategoryForm(request.POST or None, instance=instance)

        if request.method == 'POST' and form.is_valid():
            form.save()
            messages.success(request, message_text)
            return redirect('product:create_category')
  

        datas = Category.objects.all().order_by('-created_at')
        paginator = Paginator(datas, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    except ProgrammingError as e:    
        return redirect('core:home')

    return render(request, 'product/manage_category.html', {
        'form': form,
        'instance': instance,
        'datas': datas,
        'page_obj': page_obj
    })






def manage_product(request, id=None):
    if request.method == 'POST' and 'delete_id' in request.POST:
        instance = get_object_or_404(Product, id=request.POST.get('delete_id'))
        instance.delete()
        messages.success(request, "Deleted successfully")
        return redirect('product:create_product')

    instance = get_object_or_404(Product, id=id) if id else None
    message_text = "updated successfully!" if id else "added successfully!"
    form = AddProductForm(request.POST or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, message_text)
        return redirect('product:create_product')

    datas = Product.objects.all().order_by('-created_at')
    paginator = Paginator(datas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'product/manage_product.html', {
        'form': form,
        'instance': instance,
        'datas': datas,
        'page_obj': page_obj
    })



def product_data(request,product_id):
    product_instance = get_object_or_404(Product,id=product_id)
    return render(request,'product/product_data.html',{'product_instance':product_instance})
