
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import uuid
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from openpyxl import Workbook
from io import BytesIO
from django.http import HttpResponse

from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4,letter
from reportlab.pdfgen import canvas
from django.utils import timezone
import os
from django.conf import settings
from datetime import datetime,timedelta

from.forms import EditAttendanceForm,MonthYearForm,AttendanceForm,AddCompanyForm,ManageLocationForm,UpdateLocationForm,NoticeForm
from .models import EmployeeRecordChange,MonthlySalaryReport,AttendanceModel,Notice,Location,Company

from .forms import CommonFilterForm
from core.models import Employee
from core.forms import AddEmployeeForm
from django.db.models.signals import pre_save
from django.dispatch import receiver

from.forms import ManageDepartmentForm,ManagePositionForm
from.models import Department,Position


@login_required
def dashboard(request):
    return render(request,'core/dashboard.html')

@login_required
def home(request):
    return render(request,'core/home.html')

@login_required
def core_dashboard(request):
    return render(request,'core/core_dashboard.html')

@login_required
def only_core_dashboard(request):
    return render(request,'core/only_core_dashboard.html')


@login_required
def all_qc(request):
    return render(request,'core/all_qc.html')


@login_required
def manage_department(request, id=None):
    datas = Department.objects.all().order_by('-created_at')
    if request.method == 'POST' and 'delete_id' in request.POST:
        instance = get_object_or_404(Department, id=request.POST.get('delete_id'))
        instance.delete()
        messages.success(request, "Deleted successfully")
        return redirect('core:manage_department')

    instance = get_object_or_404(Department, id=id) if id else None
    message_text = "updated successfully!" if id else "added successfully!"  
    form = ManageDepartmentForm(request.POST or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        custom_name = form.cleaned_data.get('custom_department_name')
        name = form.cleaned_data.get('name')
        if custom_name and name:
            messages.error(
                request, 
                "Please either choose an existing department or provide a custom name, not both."
            )
            return redirect('core:manage_position')
    
        if custom_name: 
            department, created = Department.objects.get_or_create(
                name=custom_name,
                defaults={'description': form.cleaned_data.get('description')}
            )
            if created:
                messages.success(request, f"Custom department '{custom_name}' added successfully!")
            else:
                messages.warning(request, f"Department '{custom_name}' already exists.")
        else:
            form.save()
            messages.success(request, message_text)

        return redirect('core:manage_department')

    paginator = Paginator(datas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/manage_department.html', {
        'form': form,
        'instance': instance,
        'datas': datas,
        'page_obj': page_obj
    })



@login_required
def manage_position(request, id=None):
    datas = Position.objects.all().order_by('-created_at')

    if request.method == 'POST' and 'delete_id' in request.POST:
        instance = get_object_or_404(Position, id=request.POST.get('delete_id'))
        instance.delete()
        messages.success(request, "Deleted successfully")
        return redirect('core:manage_position')

    instance = get_object_or_404(Position, id=id) if id else None
    message_text = "updated successfully!" if id else "added successfully!"
    form = ManagePositionForm(request.POST or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        custom_name = form.cleaned_data.get('custom_position_name')
        department = form.cleaned_data.get('department')
        name = form.cleaned_data.get('name')

        if custom_name and name:
            messages.error(
                request, 
                "Please either choose an existing position or provide a custom position name, not both."
            )
            return redirect('core:manage_position')

        if custom_name:
            if not department:
                messages.error(request, "Please select a department for the custom position.")
                return redirect('core:manage_position')
            position, created = Position.objects.get_or_create(
                department=department,
                name=custom_name,
                defaults={'description': form.cleaned_data.get('description')}
            )
            if created:
                messages.success(request, f"Custom position '{custom_name}' added successfully!")
            else:
                messages.warning(request, f"Position '{custom_name}' already exists in this department.")
        else:
            form.save()
            messages.success(request, message_text)

        return redirect('core:manage_position')

    paginator = Paginator(datas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/manage_position.html', {
        'form': form,
        'instance': instance,
        'datas': datas,
        'page_obj': page_obj
    })





@login_required
def manage_company(request, id=None):
    if request.method == 'POST' and 'delete_id' in request.POST:
        instance = get_object_or_404(Company, id=request.POST.get('delete_id'))
        instance.delete()
        messages.success(request, "Deleted successfully")
        return redirect('core:create_company')

    instance = get_object_or_404(Company, id=id) if id else None
    message_text = "updated successfully!" if id else "added successfully!"
    form = AddCompanyForm(request.POST or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, message_text)
        return redirect('core:create_company')

    datas = Company.objects.all().order_by('-created_at')
    paginator = Paginator(datas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/manage_company.html', {
        'form': form,
        'instance': instance,
        'datas': datas,
        'page_obj': page_obj
    })



from .forms import ManageLocationForm


@login_required
def manage_location(request, id=None):
    datas = Location.objects.all().order_by('-created_at')

    if request.method == 'POST' and 'delete_id' in request.POST:
        instance = get_object_or_404(Location, id=request.POST.get('delete_id'))
        instance.delete()
        messages.success(request, "Location deleted successfully.")
        return redirect('core:manage_location')

    instance = get_object_or_404(Location, id=id) if id else None
    message_text = "Location updated successfully!" if id else "Location added successfully!"

    form = ManageLocationForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        custom_location_name = form.cleaned_data.get('custom_location_name')
        company = form.cleaned_data.get('company')
        name = form.cleaned_data.get('name')

        if custom_location_name and name:
            messages.error(
                request, 
                "Please either choose an existing location or provide a custom location name, not both."
            )
            return redirect('core:manage_location')

        if custom_location_name:
            if not company:
                messages.error(request, "Please select a company for the custom location.")
                return redirect('core:manage_location')

            location, created = Location.objects.get_or_create(
                company=company,
                name=custom_location_name,
                defaults={'description': form.cleaned_data.get('description')}
            )
            if created:
                messages.success(request, f"Custom location '{custom_location_name}' added successfully!")
            else:
                messages.warning(request, f"Location '{custom_location_name}' already exists for the selected company.")
        else:
            form.save()
            messages.success(request, message_text)

        return redirect('core:create_location')

    paginator = Paginator(datas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/manage_location.html', {
        'form': form,
        'instance': instance,
        'page_obj': page_obj
    })



@login_required
def manage_employee(request, id=None):
    if request.method == 'POST' and 'delete_id' in request.POST:
        instance = get_object_or_404(Employee, id=request.POST.get('delete_id'))
        instance.delete()
        messages.success(request, "Deleted successfully")
        return redirect('core:view_employee')

    instance = get_object_or_404(Employee, id=id) if id else None
    message_text = "updated successfully!" if id else "added successfully!"  
    form = AddEmployeeForm(request.POST or None, request.FILES or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        form_intance=form.save(commit=False)
        form_intance.save()        
        messages.success(request, message_text)
        return redirect('core:create_employee')

    datas = Employee.objects.all().order_by('-created_at')
    paginator = Paginator(datas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/manage_employee.html', {
        'form': form,
        'instance': instance,
        'datas': datas,
        'page_obj': page_obj
    })




@login_required
def add_employee(request):
    if request.method == 'POST':   
        form = AddEmployeeForm(request.POST, request.FILES)
        if form.is_valid():   
            form_intance=form.save(commit=False)
            form_intance.user = request.user
            form_intance.save()
            return redirect('core:view_employee')
    else:     
        form = AddEmployeeForm()
    return render(request, 'core/add_employee_form.html', {'form': form})




@login_required
def update_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        form = AddEmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form_intance=form.save(commit=False)
            form_intance.user = request.user
            form_intance.save()
            return redirect('core:view_employee') 
    else:
        form = AddEmployeeForm(instance=employee)
    return render(request, 'core/add_employee_form.html', {'form': form})


@login_required
def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        if request.POST.get('confirm') == 'yes': 
            employee.delete()
            messages.success(request, 'Employee deleted successfully.')
            return redirect('core:view_employee')  
        else:
            return redirect('core:view_employee')
    return render(request, 'core/delete_record.html', {'employee': employee})



@login_required
def view_employee(request):
    employee_name = None
    employee_records = Employee.objects.all().order_by('-created_at')

    form=CommonFilterForm(request.GET or None)

    if form.is_valid():
        employee_name = form.cleaned_data['employee_name']
        if employee_name:
            employee_records=employee_records.filter(name=employee_name)

    paginator = Paginator(employee_records, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    form=CommonFilterForm()
    return render(request, 'core/view_employee.html', 
    {
        'employee_records': employee_records,
        'form':form,
        'page_obj':page_obj
    })



@login_required
def employee_list(request):
    employees = Employee.objects.all().order_by('-created_at') 
    days=None
    start_date=None
    end_date =None
    name = None

   
    form= CommonFilterForm(request.GET or None)

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        name = form.cleaned_data.get('employee_name')

        if name:
            employees = employees.filter(id=name.id)
        
        if start_date and end_date:
             employees =  employees.filter(created_at__range=(start_date, end_date))
        elif days:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            employees=  employees.filter(created_at__range=(start_date, end_date))

    paginator = Paginator(employees, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form = CommonFilterForm()


    return render(request,'core/employee_list.html', 
        {
        'employees': employees,
        'page_obj':page_obj,
        'form':form,
         'days':days,
         'start_date':start_date,
         'end_date':end_date,
         'name':name,    

        })





@login_required
@receiver(pre_save, sender=Employee)
def log_employee_changes(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Employee.objects.get(pk=instance.pk)
        for field in instance._meta.fields:
            old_value = getattr(old_instance, field.attname)
            new_value = getattr(instance, field.attname)
            if old_value != new_value:
                EmployeeRecordChange.objects.create(
                    employee=instance,
                    field_name=field.attname,
                    old_value=str(old_value),
                    new_value=str(new_value)
                )




@login_required
def view_employee_changes(request): 
    changes = EmployeeRecordChange.objects.all()
    history =  changes.all()
    return render(request, 'core/employee_change_record.html', {'changes': changes,'history':history})


@login_required
def view_employee_changes_single(request, employee_id): 
    employee = get_object_or_404(Employee, pk=employee_id)
    changes_single = EmployeeRecordChange.objects.filter(employee=employee)
    history =  changes_single.all()
    return render(request, 'core/employee_change_record.html', {'changes_single': changes_single,'history':history})




@login_required
def download_employee_changes(request): 
    employee_changes = EmployeeRecordChange.objects.all()
    workbook = Workbook()
    worksheet = workbook.active
    headers = ['Employee ID', 'Field Name', 'Old Value', 'New Value']
    worksheet.append(headers)
    for change in employee_changes:
        row = [change.employee_id, change.field_name, change.old_value, change.new_value]
        worksheet.append(row)
    excel_file = BytesIO()
    workbook.save(excel_file)
    excel_file.seek(0)
    response = HttpResponse(
        excel_file.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=employee_changes.xlsx'
    return response



@login_required
def attendance_input(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()         
            return redirect('core:view_attendance')
        else:
            print(form.errors)  
    else:
        form = AttendanceForm()    
    return render(request, 'core/attendance_form.html', {'form': form})


@login_required
def view_attendance(request):
    attendance_records = AttendanceModel.objects.all()
    return render(request, 'core/view_attendance.html', {'attendance_records': attendance_records})


@login_required
def update_attendance(request, employee_id):
    employee = get_object_or_404(AttendanceModel, id=employee_id) 
    print(employee)  
    if request.method == 'POST':
        form =  EditAttendanceForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('core:view_attendance')  
    else:
        form =  EditAttendanceForm(instance=employee)
    return render(request, 'core/attendance_form.html', {'form': form,'employee':employee})



salary_month=None
salary_year = None 

@login_required
def create_salary(request):
    global salary_month,salary_year
    salary_month = request.GET.get('month')  
    salary_year = request.GET.get('year')  
    salary = None

    if salary_month and salary_year: 
        month = int(salary_month)
        year = int(salary_year)

        employees = Employee.objects.all()

        for employee in employees:
            total_salary = (
                employee.basic_salary +
                employee.house_allowance +
                employee.medical_allowance +
                employee.transportation_allowance +
                employee.bonus
            )

            MonthlySalaryReport.objects.update_or_create(
                employee=employee,
                month=month,
                year=year,
                defaults={'total_salary': total_salary}
            )

        salary = MonthlySalaryReport.objects.filter(month=month, year=year)

    form = MonthYearForm()

    context = {'form': form, 'salary': salary, 'month': salary_month, 'year': salary_year}
    return render(request, 'core/create_monthly_salary.html', context)



def generate_salary_sheet(month, year):   
    salary_reports = MonthlySalaryReport.objects.filter(month=month, year=year)
    
    salary_sheet = []
    for report in salary_reports: 
        if isinstance(report.employee, Employee):
            total_salary = report.total_salary
            salary_sheet.append({
                'employee': report.employee,
                'total_salary': total_salary
            })
        else:
            print(f"Invalid employee reference in report: {report}")
    
    return salary_sheet




@login_required
def download_salary(request):
    global salary_month,salary_year   

    if not salary_month or not salary_year:
        messages.error(request, "Month and Year must be provided to download the salary report.")
        return redirect('core:create_salary')

    try:
        month = int(salary_month)
        year = int(salary_year)
    except ValueError:
        messages.error(request, "Invalid Month or Year format.")
        return redirect('core:create_salary') 

    salary_sheet = generate_salary_sheet(month, year)

    if not salary_sheet:
        messages.error(request, "No salary data found for the selected month and year.")
        return redirect('core:create_salary')

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Salary Report'

    headers = ['Employee ID', 'Name', 'Total Salary']
    worksheet.append(headers)

    for entry in salary_sheet:
        employee = entry['employee']
        row = [
            employee.employee_code,
            employee.name,
            entry['total_salary']
        ]
        worksheet.append(row)

    excel_file = BytesIO()
    workbook.save(excel_file)
    excel_file.seek(0)

    response = HttpResponse(
        excel_file.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=salary_report.xlsx'
    return response




@login_required
def generate_pay_slip(request, employee_id): 
    employee = Employee.objects.get(id=employee_id)   
    envelope_size = (3.625 * 72, 5.5 * 72) 
    employee = Employee.objects.get(id=employee_id)  
    if employee.gender == 'Male':
            prefix = 'Mr.'
            prefix2 = 'his'
    elif employee.gender == 'Female':
            prefix = 'Mrs.'
            prefix2 = 'her'
    else:
            prefix = '' 
            prefix2 =''   
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pay_slip_{employee_id}.pdf"'    
    pdf_canvas = canvas.Canvas(response, pagesize=envelope_size)  
    pdf_canvas.setFont("Helvetica", 10)
    pdf_canvas.setFillColor('blue')
    pdf_canvas.drawString(50, 360, f" Mymeplus Technology Limited")
    pdf_canvas.setFont("Helvetica-Bold", 10)
    pdf_canvas.setFillColor('black')
    pdf_canvas.drawString(50, 330, f"Date: {timezone.now().date()}")
    pdf_canvas.setFont("Helvetica", 10)
    pdf_canvas.drawString(50, 300, f"Employee Code: {employee.employee_code}")
    pdf_canvas.drawString(50, 280, f"Name: {employee.name}")
    pdf_canvas.drawString(50, 260, f"Position: {employee.position}")
    pdf_canvas.drawString(50, 240, f"Department: {employee.department}")
    pdf_canvas.drawString(50, 220, f"Employee Level: {employee.employe_level}")   
    pdf_canvas.drawString(50, 200, f"Basic Salary: {employee.basic_salary}")
    pdf_canvas.drawString(50, 180, f"House Allowance: {employee.house_allowance}")
    pdf_canvas.drawString(50, 160, f"Medical Allowance: {employee.medical_allowance}")
    pdf_canvas.drawString(50, 140, f"Transportation Allowance: {employee.transportation_allowance}")
    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawString(50, 110, f"Pay Slip for {prefix} {employee.first_name} {employee.last_name}")  
    pdf_canvas.setFont("Helvetica", 10)
    cfo_employee = Employee.objects.filter(position__name='CFO').first()
    if cfo_employee:
        pdf_canvas.drawString(50, 70, f"Autorized Signature________________")  
        pdf_canvas.drawString(80, 50, f"Name:{cfo_employee.name}")  
        pdf_canvas.drawString(80, 30, f"Designation:{cfo_employee.position}")  
    else:
        pdf_canvas.drawString(50, 70, f"Autorized Signature________________")  
        pdf_canvas.drawString(80, 50, f"Name:........") 
        pdf_canvas.drawString(80, 30, f"Designation:.....") 
    pdf_canvas.setFont("Helvetica-Bold", 7)
    pdf_canvas.setFillColor('green')
    pdf_canvas.drawString(30, 15, f"Signature is not required due to computerized authorization")  
    pdf_canvas.setFillColor('yellow') 
    pdf_canvas.rect(5, 5, 250,385)
    pdf_canvas.showPage()
    pdf_canvas.save()    
    return response



@login_required
def generate_salary_certificate(request, employee_id):  
    a4_size = A4    
    employee = Employee.objects.get(id=employee_id)   
    if employee.gender == 'Male':
            prefix = 'Mr.'
            prefix2 = 'his'
    elif employee.gender == 'Female':
            prefix = 'Mrs.'
            prefix2 = 'her'
    else:
            prefix = '' 
            prefix2 =''   

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="salary_certificate_{employee_id}.pdf"'
    pdf_canvas = canvas.Canvas(response, pagesize=a4_size)
     
    logo_path = 'D:/SCM/dscm/media/logo.png'  
        
    logo_width = 60 
    logo_height = 60  
    pdf_canvas.drawImage(logo_path, 50, 750, width=logo_width, height=logo_height) 
   
    spacing1 = 15
    y_space = 700
   
    pdf_canvas.setFont("Helvetica", 12) 
    y_space -= spacing1
    pdf_canvas.drawString(50,  y_space, "mymeplus Technology Limited")
    y_space -= spacing1
    pdf_canvas.drawString(50,  y_space, "House#39, Road#15, Block#F, Bashundhara R/A, Dhaka-1229")
    y_space -= spacing1
    pdf_canvas.drawString(50,  y_space, "Phone:01842800705")
    y_space -= spacing1
    pdf_canvas.drawString(50,  y_space, "email: hkobir@mymeplus.com")
    y_space -= spacing1
    pdf_canvas.drawString(50,  y_space, "website: www.mymeplus.com")
    current_date = datetime.now().strftime("%Y-%m-%d")
    pdf_canvas.drawString(50, 600, f"Date: {current_date}") 
    pdf_canvas.drawString(50, 560, f"Salary Certificate for {prefix} {employee.first_name} {employee.last_name}")
    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawString(200, 500, "To Whom It May Concern")     
    pdf_canvas.setFont("Helvetica", 10)
   
  
    spacing1 = 15
    y_space = 450 

    pdf_canvas.drawString(50, 450, f"This is to certify that {prefix} {employee.name} is working in the {employee.department} department since {employee.joining_date}, {prefix2} monthly")
    y_space -= spacing1
    pdf_canvas.drawString(50, y_space, f" remuneration is as follows:")       
    y_space -= spacing1
    pdf_canvas.drawString(150, y_space, f"Basic Salary: {employee.basic_salary}")
    y_space -= spacing1
    pdf_canvas.drawString(150, y_space, f"House Allowance: {employee.house_allowance}")
    y_space -= spacing1
    pdf_canvas.drawString(150, y_space, f"Medical Allowance: {employee.medical_allowance}")
    y_space -= spacing1
    pdf_canvas.drawString(150, y_space, f"Transportation Allowance: {employee.transportation_allowance}")
    y_space -= spacing1
    pdf_canvas.drawString(150, y_space, f"Festival Bonus: {employee.bonus}")   
    y_space -= spacing1+20
    pdf_canvas.drawString(50, y_space, f"The total monthly remuneration of {employee.name} amounts to {employee.gross_monthly_salary}")
    y_space -= spacing1
    pdf_canvas.drawString(50, y_space, f"This certificate is issued upon request of {employee.name} for {prefix2} intended purpose. Please do not hesitate to contact us")
    y_space -= spacing1
    pdf_canvas.drawString(50, y_space, f"if further clarification is required.")
    pdf_canvas.drawString(50, 250, f"Sincerely,")
    cfo_employee = Employee.objects.filter(position__name='CFO').first()
    if cfo_employee:
        pdf_canvas.drawString(50, 150, f"Autorized Signature________________")  
        pdf_canvas.drawString(50, 135, f"Name:{cfo_employee.name}")  
        pdf_canvas.drawString(50, 120, f"Designation:{cfo_employee.position}")  
    else:
        pdf_canvas.drawString(50, 150, f"Autorized Signature________________")  
        pdf_canvas.drawString(50, 135, f"Name:........") 
        pdf_canvas.drawString(50, 120, f"Designation:.....")  
    pdf_canvas.setFont("Helvetica-Bold", 10)
    pdf_canvas.setFillColor('green')
    pdf_canvas.drawString(50,80, f"Signature is not mandatory due to computerized authorization")
    pdf_canvas.showPage()
    pdf_canvas.save()    
    return response


@login_required
def generate_experience_certificate(request, employee_id):  
    a4_size = A4    
    employee = Employee.objects.get(id=employee_id)       
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="experience_certificate_{employee_id}.pdf"'
    pdf_canvas = canvas.Canvas(response, pagesize=a4_size)
    if employee.gender == 'Male':
            prefix = 'Mr.'
            prefix2 = 'his'
            prefix3 ='him'
    elif employee.gender == 'Female':
            prefix = 'Mrs.'
            prefix2 = 'her'
            prefix3 = 'her'
    else:
            prefix = '' 
            prefix2 =''
            prefix3 =''

    logo_path = 'D:/SCM/dscm/media/logo.png'  
        
    logo_width = 60 
    logo_height = 60  
    pdf_canvas.drawImage(logo_path, 50, 750, width=logo_width, height=logo_height) 

    spacing1 = 15
    y_space = 730
    pdf_canvas.setFont("Helvetica", 12) 
    y_space -= spacing1
    pdf_canvas.drawString(50,  y_space, "mymeplus Technology Limited")
    y_space -= spacing1
    pdf_canvas.drawString(50,  y_space, "House#39, Road#15, Block#F, Bashundhara R/A, Dhaka-1229")
    y_space -= spacing1
    pdf_canvas.drawString(50,  y_space, "Phone:01842800705")
    y_space -= spacing1
    pdf_canvas.drawString(50,  y_space, "email: hkobir@mymeplus.com")
    y_space -= spacing1
    pdf_canvas.drawString(50,  y_space, "website: www.mymeplus.com")
    pdf_canvas.setFont("Helvetica", 12)
    current_date = datetime.now().strftime("%Y-%m-%d")
    pdf_canvas.drawString(50, 570,f"Date: {current_date}")   
    pdf_canvas.drawString(50, 535,  f"Experience Certificate for {prefix} {employee.first_name} {employee.last_name}")
    pdf_canvas.drawString(50, 500, f"This is to certify that {prefix} {employee.first_name}  {employee.last_name} was employed at from {employee.joining_date} to {employee.resignation_date}.")
    pdf_canvas.drawString(50, 485, f"During {prefix2} tenure, {employee.name} held the position of {employee.position} as {prefix2} last designation and performed {prefix2}")
    pdf_canvas.drawString(50, 470, f"duties with dedication and professionalism. We wish {prefix3} all the best for {prefix2} future endeavors.")     
    cfo_employee = Employee.objects.filter(position__name='CFO').first()
    if cfo_employee:
        pdf_canvas.drawString(50, 350, f"Autorized Signature________________")  
        pdf_canvas.drawString(50, 335, f"Name:{cfo_employee.name}")  
        pdf_canvas.drawString(50, 320, f"Designation:{cfo_employee.position}")  
    else:
        pdf_canvas.drawString(50, 350, f"Autorized Signature________________")  
        pdf_canvas.drawString(50, 335, f"Name:........") 
        pdf_canvas.drawString(50, 320, f"Designation:.....")  
    pdf_canvas.setFont("Helvetica-Bold", 10)
    pdf_canvas.setFillColor('green')
    pdf_canvas.drawString(50,280, f"Signature is not mandatory due to computerized authorization")  
    pdf_canvas.showPage()
    pdf_canvas.save()    
    return response




@login_required
def add_notice(request):
    if request.method == 'POST':
        form = NoticeForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('core:view_notices')
    else:
        form = NoticeForm()
    return render(request, 'core/add_notice.html', {'form': form})


@login_required
def view_notices(request):
    notices = Notice.objects.all().order_by('-created_at')
    form = NoticeForm()
    return render(request, 'core/view_notices.html', {'notices': notices, 'form': form})