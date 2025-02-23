
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
from clients.models import SubscriptionPlan

from.models import CompanyPolicy,SalaryStructure
from.forms import CompanyPolicyForm,SalaryStructureForm
from .forms import ManageLocationForm

from django.template.loader import render_to_string
from django.core.mail import EmailMessage,send_mail

import base64


@login_required
def dashboard(request):
    plans = SubscriptionPlan.objects.all().order_by('duration')
    for plan in plans:
        plan.features_list = plan.features.split(',')

    modules = [
    {"name": "SCM Module", "icon": "fas fa-truck", "description": "Optimize your supply chain.", "link": "core:home"},
    {"name": "Core HR Management", "icon": "fas fa-cogs", "description": "Streamline core business processes.", "link": "core:only_core_dashboard"},
    {"name": "Appraisal Automation", "icon": "fas fa-chart-line", "description": "Automate performance reviews.", "link": "tasks:tasks_dashboard"},
    {"name": "Recruitment Automation", "icon": "fas fa-file-signature", "description": "Simplify hiring workflows.", "link": "recruitment:recruitment_dashboard"},
    {"name": "Leave management", "icon": "fas fa-users", "description": "Automate entire leave management system and established association with others.., .", "link": "recruitment:recruitment_dashboard"},
    {"name": "Transport Management", "icon": "fas fa-bus", "description": "Manage transport and fleet.", "link": "transport:transport_dashboard"},
]

    return render(request,'core/dashboard.html',{'plans':plans,'modules':modules})

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
def manage_department(request):
    departments = Department.objects.all().order_by('-created_at')  
    form = ManageDepartmentForm(request.POST or None)

    if request.method == 'POST':
        if 'entity_submit' in request.POST:  
            if form.is_valid():
                department = form.save(commit=False)
                department.user = request.user  
                department.save()
                messages.success(request, "Department added successfully.")
                return redirect('core:manage_department')  
            else:
                messages.error(request, "Form is invalid. Please check the details and try again.")

        elif 'action' in request.POST:
            print(request.POST)  
            action = request.POST.get('action')
            entity_id = int(request.POST.get('entity_id', 0))

            if not entity_id: 
                messages.error(request, "Invalid entry ID provided.")
                return redirect('core:manage_department')

            if action == 'update':
                entity_obj = get_object_or_404(Department, id=entity_id)
                form = ManageDepartmentForm(request.POST, instance=entity_obj)
                if form.is_valid():
                    updated_entity = form.save(commit=False)
                    updated_entity.user = request.user
                    updated_entity.save()
                    messages.success(request, "Department updated successfully.")
                    return redirect('core:manage_department')
                else:
                    messages.error(request, "Form is invalid. Please check the details.")
            elif action == 'delete':
                entity_obj = get_object_or_404(Department, id=entity_id)
                entity_obj.delete()
                messages.success(request, "Department deleted successfully.")
                return redirect('core:manage_department')


    paginator = Paginator(departments, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,'core/manage_department.html',{'form': form, 'page_obj': page_obj})





@login_required
def manage_position(request, id=None):  
    instance = get_object_or_404(Position, id=id) if id else None
    message_text = "updated successfully!" if id else "added successfully!"  
    form = ManagePositionForm(request.POST or None, request.FILES or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        form_intance=form.save(commit=False)
        form_intance.user = request.user
        form_intance.save()   
        form.save_m2m()     
        messages.success(request, message_text)
        return redirect('core:create_position')  
    else:
        print(form.errors)

    datas = Position.objects.all().order_by('-created_at')
    paginator = Paginator(datas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form = ManagePositionForm(instance=instance)
    return render(request, 'core/manage_position.html', {
        'form': form,
        'instance': instance,
        'datas': datas,
        'page_obj': page_obj
    })


@login_required
def delete_position(request, id):
    instance = get_object_or_404(Position, id=id)
    if request.method == 'POST':
        instance.delete()
        messages.success(request, "Deleted successfully!")
        return redirect('core:create_position')  

    messages.warning(request, "Invalid delete request!")
    return redirect('core:create_position') 


def position_details(request,id):
    position_instance = get_object_or_404(Position,id=id)
    return render(request,'core/position_details.html',{'position_instance':position_instance})



from.models import JobDescription,JobRequirement
from.forms import JobDescriptionForm,JobRequirementForm



@login_required
def manage_job_description(request, id=None):  
    datas=[]
    position=None
    department = None
    
    instance = get_object_or_404(JobDescription, id=id) if id else None
    message_text = "updated successfully!" if id else "added successfully!"  
    form = JobDescriptionForm(request.POST or None, request.FILES or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        position = form.cleaned_data['position']
        department = form.cleaned_data['department']
        form_intance=form.save(commit=False)
        form_intance.save()        
        messages.success(request, message_text)
        return redirect('core:create_job_description')  
    
    if instance:
        datas = JobDescription.objects.filter(position=instance.position,department=instance.department).order_by('-created_at')
    elif position and department:
         datas = JobDescription.objects.filter(position=position,department=department).order_by('-created_at')
    else:
        datas = JobDescription.objects.all().order_by('-created_at')

    paginator = Paginator(datas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form = JobDescriptionForm(instance=instance)
    return render(request, 'core/manage_job_description.html', {
        'form': form,
        'instance': instance,
        'datas': datas,
        'page_obj': page_obj
    })


@login_required
def delete_job_descriptiont(request, id):
    instance = get_object_or_404(JobDescription, id=id)
    if request.method == 'POST':
        instance.delete()
        messages.success(request, "Deleted successfully!")
        return redirect('core:create_job_description')    

    messages.warning(request, "Invalid delete request!")
    return redirect('core:create_job_description')  



@login_required
def manage_job_requirement(request, id=None):  
    instance = get_object_or_404(JobRequirement, id=id) if id else None
    message_text = "updated successfully!" if id else "added successfully!"  
    form = JobRequirementForm(request.POST or None, request.FILES or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        form_intance=form.save(commit=False)
        form_intance.save()        
        messages.success(request, message_text)
        return redirect('core:create_job_requirement')  

    datas = JobRequirement.objects.all().order_by('-created_at')
    paginator = Paginator(datas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = JobRequirementForm( instance=instance)
    return render(request, 'core/manage_job_requirement.html', {
        'form': form,
        'instance': instance,
        'datas': datas,
        'page_obj': page_obj
    })


@login_required
def delete_job_requirement(request, id):
    instance = get_object_or_404(JobRequirement, id=id)
    if request.method == 'POST':
        instance.delete()
        messages.success(request, "Deleted successfully!")
        return redirect('core:create_job_requirement')    

    messages.warning(request, "Invalid delete request!")
    return redirect('core:create_job_requirement')  





@login_required
def create_company(request, id=None):  
    instance = get_object_or_404(Company, id=id) if id else None
    message_text = "updated successfully!" if id else "added successfully!"  
    form = AddCompanyForm(request.POST or None, request.FILES or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        form_intance=form.save(commit=False)
        form_intance.save()        
        messages.success(request, message_text)
        return redirect('core:create_company')  

    datas = Company.objects.all().order_by('-created_at')
    paginator = Paginator(datas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/create_company.html', {
        'form': form,
        'instance': instance,
        'datas': datas,
        'page_obj': page_obj
    })


@login_required
def delete_company(request, id):
    instance = get_object_or_404(Company, id=id)
    if request.method == 'POST':
        instance.delete()
        messages.success(request, "Deleted successfully!")
        return redirect('core:create_company')   

    messages.warning(request, "Invalid delete request!")
    return redirect('core:create_company')   





@login_required
def manage_location(request):
    entities = Location.objects.all().order_by('-created_at')  
    companies = Company.objects.all()
    form =ManageLocationForm(request.POST or None)

    if request.method == 'POST':
        if 'entity_submit' in request.POST:  
            if form.is_valid():
                entity = form.save(commit=False)
                entity.user = request.user  
                entity.save()
                messages.success(request, "added successfully.")
                return redirect('core:manage_location')  
            else:
                messages.error(request, "Form is invalid. Please check the details and try again.")

        elif 'action' in request.POST:           
            action = request.POST.get('action')
            print(request.POST)
            entity_id = int(request.POST.get('entity_id', 0))

            if not entity_id: 
                messages.error(request, "Invalid entry ID provided.")
                return redirect('core:manage_location')  

            if action == 'update':
                entity_obj = get_object_or_404(Location, id=entity_id)              
                form =  ManageLocationForm(request.POST, instance=entity_obj)
                if form.is_valid():
                    updated_entity = form.save(commit=False)
                    updated_entity.user = request.user
                    updated_entity.save()
                    messages.success(request, "updated successfully.")
                    return redirect('core:manage_location')  
                else:                  
                    messages.error(request, "Form is invalid. Please check the details.")
            elif action == 'delete':
                entity_obj = get_object_or_404(Location, id=entity_id)
                entity_obj.delete()
                messages.success(request, "deleted successfully.")
                return redirect('core:manage_location')  

    paginator = Paginator(entities, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'core/manage_location.html',{'form': form, 'page_obj': page_obj,'companies':companies})


@login_required
def manage_company_policy(request, id=None):  
    instance = get_object_or_404(CompanyPolicy, id=id) if id else None
    message_text = "updated successfully!" if instance else "added successfully!"    
    form = CompanyPolicyForm(request.POST or None, request.FILES or None, instance=instance)

    if request.method == 'POST':
        form = CompanyPolicyForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form_instance = form.save(commit=False)        
            form_instance.user = request.user
            form_instance.save()    
            messages.success(request, message_text)
            return redirect('core:create_company_policy')  # Redirect ensures form is cleared

    # If a new entry is being created (no id), clear the form
    if not id and request.method != "POST":
        form = CompanyPolicyForm()  

    datas = CompanyPolicy.objects.all().order_by('-created_at')
    paginator = Paginator(datas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/manage_company_policy.html', {
        'form': form,  
        'instance': instance,
        'datas': datas,
        'page_obj': page_obj
    })


@login_required
def delete_company_policy(request, id):
    instance = get_object_or_404(CompanyPolicy, id=id)
    if request.method == 'POST':
        instance.delete()
        messages.success(request, "Deleted successfully!")
        return redirect('core:create_company_policy')  

    messages.warning(request, "Invalid delete request!")
    return redirect('core:create_company_policy')  



@login_required
def manage_salary_structure(request, id=None):
    instance = get_object_or_404(SalaryStructure, id=id) if id else None
    message_text = "updated successfully!" if instance else "added successfully!"

    form = SalaryStructureForm(request.POST or None, request.FILES or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        form_instance = form.save(commit=False)
        form_instance.user = request.user  
            
        form_instance.save()
        messages.success(request, message_text)     
        return redirect('core:create_salary_structure')
  
    datas = SalaryStructure.objects.all().order_by('-created_at')    
    paginator = Paginator(datas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

 
    return render(request, 'core/manage_salary_structure.html', {
        'form': form,
        'instance': instance,
        'datas': datas,
        'page_obj': page_obj
    })



@login_required
def delete_salary_structure(request, id):
    instance = get_object_or_404(SalaryStructure, id=id)
    if request.method == 'POST':
        instance.delete()
        messages.success(request, "Deleted successfully!")
        return redirect('core:create_salary_structure') 

    messages.warning(request, "Invalid delete request!")
    return redirect('core:create_salary_structure')


from.models import Festival,PerformanceBonus
from.forms import FestivalForm,PeformanceBonusForm

@login_required
def manage_festival(request, id=None):
    instance = get_object_or_404(Festival, id=id) if id else None
    message_text = "updated successfully!" if instance else "added successfully!"

    form = FestivalForm(request.POST or None, request.FILES or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        form_instance = form.save(commit=False)
        form_instance.user = request.user  
            
        form_instance.save()
        messages.success(request, message_text)     
        return redirect('core:create_festival')
  
    datas = Festival.objects.all().order_by('-created_at')    
    paginator = Paginator(datas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

 
    return render(request, 'core/manage_festival.html', {
        'form': form,
        'instance': instance,
        'datas': datas,
        'page_obj': page_obj
    })



@login_required
def delete_festival(request, id):
    instance = get_object_or_404(Festival, id=id)
    if request.method == 'POST':
        instance.delete()
        messages.success(request, "Deleted successfully!")
        return redirect('core:create_festival') 

    messages.warning(request, "Invalid delete request!")
    return redirect('core:create_festival')



@login_required
def manage_performance_bonus(request, id=None):
    instance = get_object_or_404(PerformanceBonus, id=id) if id else None
    message_text = "updated successfully!" if instance else "added successfully!"

    form = PeformanceBonusForm(request.POST or None, request.FILES or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        form_instance = form.save(commit=False)
        form_instance.user = request.user  
            
        form_instance.save()
        messages.success(request, message_text)     
        return redirect('core:create_performance_bonus')
  
    datas = PerformanceBonus.objects.all().order_by('-created_at')    
    paginator = Paginator(datas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

 
    return render(request, 'core/manage_performance_bonus.html', {
        'form': form,
        'instance': instance,
        'datas': datas,
        'page_obj': page_obj
    })



@login_required
def delete_performance_bonus(request, id):
    instance = get_object_or_404(PerformanceBonus, id=id)
    if request.method == 'POST':
        instance.delete()
        messages.success(request, "Deleted successfully!")
        return redirect('core:create_performance_bonus') 

    messages.warning(request, "Invalid delete request!")
    return redirect('core:create_performance_bonus') 








@login_required
def manage_employee(request, id=None):  
    instance = get_object_or_404(Employee, id=id) if id else None
    message_text = "updated successfully!" if id else "added successfully!"  
    form = AddEmployeeForm(request.POST or None, request.FILES or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        form_intance=form.save(commit=False)
        form_intance.save()        
        messages.success(request, message_text)
        return redirect('core:manage_employee')

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
def delete_employee(request, id):
    instance = get_object_or_404(Employee, id=id)
    if request.method == 'POST':
        instance.delete()
        messages.success(request, "Deleted successfully!")
        return redirect('core:manage_employee')

    messages.warning(request, "Invalid delete request!")
    return redirect('core:manage_employee')



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
                employee.salary_structure.basic_salary +
                employee.salary_structure.hra +
                employee.salary_structure.medical_allowance +
                employee.salary_structure.conveyance_allowance +
                employee.salary_structure.festival_allowance +
                 employee.salary_structure.performance_bonus
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





def generate_pay_slip_pdf(employee): 
    buffer = BytesIO()
    envelope_size = (3.625 * 72, 5.5 * 72)  
    pdf_canvas = canvas.Canvas(buffer, pagesize=envelope_size)  
     
    if employee.gender == 'Male':
            prefix = 'Mr.'
            prefix2 = 'his'
    elif employee.gender == 'Female':
            prefix = 'Mrs.'
            prefix2 = 'her'
    else:
            prefix = '' 
            prefix2 =''   
        
    pdf_canvas.setFont("Helvetica", 10)
    pdf_canvas.setFillColor('blue')
    pdf_canvas.drawString(50, 370, f" Mymeplus Technology Limited")

    pdf_canvas.setFont("Helvetica", 10)
    pdf_canvas.setFillColor('green')
    pdf_canvas.drawString(100, 350, f"Pay Slip")


    pdf_canvas.setFont("Helvetica-Bold", 10)
    pdf_canvas.setFillColor('black')
    pdf_canvas.drawString(50, 330, f"Date: {timezone.now().date()}")
    pdf_canvas.setFont("Helvetica", 10)
    pdf_canvas.drawString(50, 300, f"Employee Code: {employee.employee_code}")
    pdf_canvas.drawString(50, 280, f"Name: {employee.name}")
    pdf_canvas.drawString(50, 260, f"Position: {employee.position}")
    pdf_canvas.drawString(50, 240, f"Department: {employee.department}")
    pdf_canvas.drawString(50, 220, f"Employee Level: {employee.employee_level}")   
    pdf_canvas.drawString(50, 200, f"Basic Salary: {employee.salary_structure.basic_salary}")
    pdf_canvas.drawString(50, 180, f"House Allowance: {employee.salary_structure.hra}")
    pdf_canvas.drawString(50, 160, f"Medical Allowance: {employee.salary_structure.medical_allowance}")
    pdf_canvas.drawString(50, 140, f"Transportation Allowance: {employee.salary_structure.conveyance_allowance}")
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

    buffer.seek(0)
    return buffer




@login_required
def  preview_pay_slip(request, employee_id):  
    employee = get_object_or_404(Employee, id=employee_id)
    pdf_buffer = generate_pay_slip_pdf(employee)    
    pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
    return render(request, "core/preview_pay_slip.html", {
        "employee": employee,
        "pdf_preview": pdf_base64,
    })



def send_pay_slip(employee):      
    if not employee.email:
        return f"Employee email not found for {employee.name}."
    pdf_buffer = generate_pay_slip_pdf(employee)   
    message = f'Dear {employee.name} , your requested salary certificate is attached herewith'
    try:
        email = EmailMessage(
            subject="Offer Letter from Our Company",
            body=message,
            from_email="yourcompany@example.com",
            to=[employee.email]
        )
        email.attach(f"Pay slip_{employee.id}.pdf", pdf_buffer.getvalue(), 'application/pdf')
        email.content_subtype = "html"
        email.send()        
      
        return f"Offer letter sent to {employee.name} successfully!"
    except Exception as e:
        return f"Error sending offer letter to {employee.name}: {str(e)}"




@login_required
def generate_and_send_pay_slip(request, employee_id): 
    employee = get_object_or_404(Employee,id=employee_id)
    message = send_pay_slip(employee)
    if "Error" in message:
        messages.error(request, message)
    else:
        messages.success(request, message)

    return redirect('core:employee_list')




def generate_salary_certificate_pdf(employee):
    buffer = BytesIO()
    pdf_canvas = canvas.Canvas(buffer, pagesize=A4)

    # Prefix logic
    if employee.gender == 'Male':
        prefix, prefix2 = 'Mr.', 'his'
    elif employee.gender == 'Female':
        prefix, prefix2 = 'Mrs.', 'her'
    else:
        prefix, prefix2 = '', ''

    # Company details and header
    logo_path = 'D:/SCM/dscm/media/logo.png'
    pdf_canvas.drawImage(logo_path, 50, 750, width=60, height=60)

    y_space = 700
    spacing1 = 15
    pdf_canvas.setFont("Helvetica", 12)
    pdf_canvas.drawString(50, y_space, "mymeplus Technology Limited")
    y_space -= spacing1
    pdf_canvas.drawString(50, y_space, "House#39, Road#15, Block#F, Bashundhara R/A, Dhaka-1229")
    y_space -= spacing1
    pdf_canvas.drawString(50, y_space, "Phone:01842800705")
    y_space -= spacing1
    pdf_canvas.drawString(50, y_space, "Email: hkobir@mymeplus.com")
    y_space -= spacing1
    pdf_canvas.drawString(50, y_space, "Website: www.mymeplus.com")

    # Date and heading
    current_date = datetime.now().strftime("%Y-%m-%d")
    pdf_canvas.drawString(50, 600, f"Date: {current_date}")
    pdf_canvas.drawString(50, 560, f"Salary Certificate for {prefix} {employee.first_name} {employee.last_name}")
    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawString(200, 500, "To Whom It May Concern")

    # Salary details
    pdf_canvas.setFont("Helvetica", 10)
    y_space = 450
    pdf_canvas.drawString(50, y_space, f"This is to certify that {prefix} {employee.name} is working in the {employee.department} department since {employee.joining_date}, {prefix2} monthly remuneration is as follows:")
    y_space -= spacing1
    pdf_canvas.drawString(150, y_space, f"Basic Salary: {employee.salary_structure.basic_salary}")
    y_space -= spacing1
    pdf_canvas.drawString(150, y_space, f"House Allowance: {employee.salary_structure.hra}")
    y_space -= spacing1
    pdf_canvas.drawString(150, y_space, f"Medical Allowance: {employee.salary_structure.medical_allowance}")
    y_space -= spacing1
    pdf_canvas.drawString(150, y_space, f"Transportation Allowance: {employee.salary_structure.conveyance_allowance}")
    y_space -= spacing1
    pdf_canvas.drawString(150, y_space, f"Festival Bonus: {employee.salary_structure.festival_allowance}")
    y_space -= spacing1 + 20
    pdf_canvas.drawString(50, y_space, f"The total monthly remuneration of {employee.name} amounts to {employee.salary_structure.gross_salary()}")
    y_space -= spacing1
    pdf_canvas.drawString(50, y_space, f"This certificate is issued upon request of {employee.name} for {prefix2} intended purpose. Please do not hesitate to contact us if further clarification is required.")

    # Authorized Signature
    pdf_canvas.drawString(50, 250, "Sincerely,")
    cfo_employee = Employee.objects.filter(position__name='CFO').first()
    if cfo_employee:
        pdf_canvas.drawString(50, 150, "Authorized Signature________________")
        pdf_canvas.drawString(50, 135, f"Name: {cfo_employee.name}")
        pdf_canvas.drawString(50, 120, f"Designation: {cfo_employee.position}")
    else:
        pdf_canvas.drawString(50, 150, "Authorized Signature________________")
        pdf_canvas.drawString(50, 135, "Name: ........")
        pdf_canvas.drawString(50, 120, "Designation: .....")

    pdf_canvas.setFont("Helvetica-Bold", 10)
    pdf_canvas.setFillColor('green')
    pdf_canvas.drawString(50, 80, "Signature is not mandatory due to computerized authorization")

    pdf_canvas.showPage()
    pdf_canvas.save()

    buffer.seek(0)
    return buffer



@login_required
def preview_salary_certificate(request, employee_id):  
    employee = get_object_or_404(Employee, id=employee_id)
    pdf_buffer = generate_salary_certificate_pdf(employee)    
    pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
    return render(request, "core/preview_salary_certificate.html", {
        "employee": employee,
        "pdf_preview": pdf_base64,
    })




def send_salary_certificate(employee):      
    if not employee.email:
        return f"Employee email not found for {employee.name}."
    pdf_buffer = generate_salary_certificate_pdf(employee)   
    message = f'Dear {employee.name} , your requested salary certificate is attached herewith'
    try:
        email = EmailMessage(
            subject="Offer Letter from Our Company",
            body=message,
            from_email="yourcompany@example.com",
            to=[employee.email]
        )
        email.attach(f"salary_certificate_{employee.id}.pdf", pdf_buffer.getvalue(), 'application/pdf')
        email.content_subtype = "html"
        email.send()        
      
        return f"Offer letter sent to {employee.name} successfully!"
    except Exception as e:
        return f"Error sending offer letter to {employee.name}: {str(e)}"




@login_required
def generate_and_send_salary_certificate(request, employee_id): 
    employee = get_object_or_404(Employee,id=employee_id)
    message = send_salary_certificate(employee)
    if "Error" in message:
        messages.error(request, message)
    else:
        messages.success(request, message)

    return redirect('core:employee_list')





def generate_experience_certificate_pdf(employee):   
    buffer = BytesIO() 
    a4_size = A4           
    pdf_canvas = canvas.Canvas(buffer,pagesize=a4_size)

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
    
    buffer.seek(0)
    return buffer




@login_required
def preview_experience_certificate(request, employee_id):  
    employee = get_object_or_404(Employee, id=employee_id)
    pdf_buffer = generate_experience_certificate_pdf(employee)    
    pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
    return render(request, "core/preview_experience_certificate.html", {
        "employee": employee,
        "pdf_preview": pdf_base64,
    })



def send_experience_certificate(employee):      
    if not employee.email:
        return f"Employee email not found for {employee.name}."
    pdf_buffer = generate_experience_certificate_pdf(employee)   
    message = f'Dear {employee.name} , your requested experience certificate is attached herewith'
    try:
        email = EmailMessage(
            subject=f"Experience certificate for {employee.name}",
            body=message,
            from_email="yourcompany@example.com",
            to=[employee.email]
        )
        email.attach(f"experience_certificate_{employee.id}.pdf", pdf_buffer.getvalue(), 'application/pdf')
        email.content_subtype = "html"
        email.send()        
      
        return f"Experience certificate sent to {employee.name} successfully!"
    except Exception as e:
        return f"Error sending Experience certificate  to {employee.name}: {str(e)}"




@login_required
def generate_and_send_experience_certificate(request, employee_id): 
    employee = get_object_or_404(Employee,id=employee_id)
    message = send_experience_certificate(employee)
    if "Error" in message:
        messages.error(request, message)
    else:
        messages.success(request, message)

    return redirect('core:employee_list')





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






##################### leave management #####################################

from .forms import LeaveApplicationForm,LeaveTypeForm
from.models import LeaveApplication,EmployeeLeaveBalance,LeaveType
from .models import EmployeeLeaveBalance

from django.urls import reverse


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



@login_required
def leave_dashboard(request):
    menu_items = [
        {'title': 'Create leave type', 'url': reverse('core:create_leave_type')},
        {'title': 'Apply for leave', 'url': reverse('core:apply_leave')},
        {'title': 'Leave application status', 'url': reverse('core:leave_history')},     
        {'title': 'Leave summary', 'url': reverse('core:leave_summary')},
        {'title': 'Pending leave application', 'url': reverse('core:pending_leave_list')},     
       
    ]
    return render(request, 'core/leave_management/leave_dashboard.html', {'menu_items': menu_items})


@login_required
def manage_leave_type(request, id=None):  
    instance = get_object_or_404(LeaveType, id=id) if id else None
    message_text = "updated successfully!" if id else "added successfully!"  
    form = LeaveTypeForm(request.POST or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        form_intance=form.save(commit=False)
        form_intance.save()        
        messages.success(request, message_text)
        return redirect('core:create_leave_type')  

    datas = LeaveType.objects.all().order_by('-created_at')
    paginator = Paginator(datas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/leave_management/manage_leave_type.html', {
        'form': form,
        'instance': instance,
        'datas': datas,
        'page_obj': page_obj
    })


@login_required
def delete_leave_type(request, id):
    instance = get_object_or_404(LeaveType, id=id)
    if request.method == 'POST':
        instance.delete()
        messages.success(request, "Deleted successfully!")
        return redirect('core:create_leave_type')   

    messages.warning(request, "Invalid delete request!")
    return redirect('core:create_leave_type')  
  



from datetime import date
def get_accrued_balance(employee, leave_type):
    balance_record, created = EmployeeLeaveBalance.objects.get_or_create(
        employee=employee,
        leave_type=leave_type,
        defaults={'balance': 0, 'carry_forward': 0}
    )

    if leave_type.accrues_monthly:
        current_month = date.today().month
        joining_month = employee.joining_date.month if employee.joining_date else 1

        eligible_months = max(0, current_month - joining_month + 1)
        max_accruable_days = leave_type.accrual_rate * eligible_months

        return min(balance_record.balance, max_accruable_days)

    return balance_record.balance



################ management commands ##############################################

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Update leave balances for all employees'

    def handle(self, *args, **kwargs):
        employees = Employee.objects.all()
        for employee in employees:
            leave_balances = EmployeeLeaveBalance.objects.filter(employee=employee)
            for balance in leave_balances:
                if balance.leave_type.accrues_monthly:
                    current_month = date.today().month
                    joining_month = employee.joining_date.month if employee.joining_date else 1
                    eligible_months = max(0, current_month - joining_month + 1)
                    max_accruable_days = balance.leave_type.accrual_rate * eligible_months

                    balance.balance = min(balance.balance, max_accruable_days)
                    balance.save()
        self.stdout.write(self.style.SUCCESS('Leave balances updated successfully!'))


class Command(BaseCommand):
    help = 'Carry forward leave balances to the next year'

    def handle(self, *args, **kwargs):
        current_year = timezone.now().year
        next_year = current_year + 1

        balances = EmployeeLeaveBalance.objects.filter(
            year=current_year,
            leave_type__allow_carry_forward=True
        )

        for balance in balances:
            max_limit = balance.leave_type.max_carry_forward_limit or 0
            carry_over_days = min(balance.balance, max_limit)

            next_year_balance, created = EmployeeLeaveBalance.objects.get_or_create(
                employee=balance.employee,
                leave_type=balance.leave_type,
                year=next_year,
                defaults={
                    'balance': balance.leave_type.annual_allowance,
                    'carry_forward': carry_over_days,
                }
            )

            if not created:
                next_year_balance.carry_forward = carry_over_days
                next_year_balance.save()

        self.stdout.write(self.style.SUCCESS('Leave balances carried forward successfully!'))

#####################################################################################################


from django.db.models import Sum
from .forms import ApprovalForm
from datetime import date
from django.db.models import Sum


@login_required
def monthly_leave_accrual_update(request):
    today = date.today()
    current_month = today.month
    current_year = today.year

    employees = Employee.objects.all()

    for employee in employees:
        leave_balances = EmployeeLeaveBalance.objects.filter(employee=employee)

        for balance_instance in leave_balances:
            leave_type = balance_instance.leave_type
            if not leave_type.accrues_monthly:
                continue

            if balance_instance.last_accrued_month == current_month:
                continue  
 
            approved_leaves = LeaveApplication.objects.filter(
                employee=employee,
                leave_type=leave_type,
                status='APPROVED',
                approved_start_date__year=current_year,
                approved_start_date__month=current_month,
            ).aggregate(total_days=Sum('approved_no_of_days'))['total_days'] or 0
 
            accrued_days = leave_type.accrual_rate
            balance_instance.balance += accrued_days
            balance_instance.balance -= approved_leaves
            if balance_instance.balance < 0:
                balance_instance.balance = 0
 
            balance_instance.last_accrued_month = current_month
            balance_instance.save()
    return HttpResponse("Monthly leave accrual updated successfully for all employees.")



@login_required
def carry_forward_leave(request):
    current_date = timezone.now()
    current_year = current_date.year
    next_year = current_year + 1


    if current_date.month != 1: 
        messages.warning(request, 'Carry forward process is only allowed in January.')
        return redirect('core:leave_dashboard')

    balances = EmployeeLeaveBalance.objects.filter(
        year=current_year,
        leave_type__allow_carry_forward=True
    )

    for balance in balances:
        max_limit = balance.leave_type.max_carry_forward_limit or 0
        carry_over_days = min(balance.balance, max_limit)

        next_year_balance, created = EmployeeLeaveBalance.objects.get_or_create(
            employee=balance.employee,
            leave_type=balance.leave_type,
            year=next_year,
            defaults={
                'balance': balance.leave_type.annual_allowance + carry_over_days,
                'carry_forward': carry_over_days,
            }
        )

        if not created:    
            next_year_balance.carry_forward = carry_over_days
            next_year_balance.balance += carry_over_days
            next_year_balance.save()

    messages.success(request, 'Eligible leave balances have been successfully carried forward!')
    return redirect('core:create_leave_type')




@login_required
def apply_leave(request):
    if request.method == 'POST':
        form = LeaveApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            start_date = form.cleaned_data['applied_start_date']
            end_date = form.cleaned_data['applied_end_date']
            leave_application = form.save(commit=False)
            employee = Employee.objects.filter(user_profile=request.user.user_profile).first()                    
            if not employee:
                messages.error(request, 'Employee record not found!')
                return redirect('core:leave_history')
            leave_application.employee = employee
            balance_record, created = EmployeeLeaveBalance.objects.get_or_create(
                employee=leave_application.employee,
                leave_type=leave_application.leave_type,
                defaults={'balance': 0}
            )
            leave_days = (end_date - start_date).days + 1
            allowed_balance = get_accrued_balance(leave_application.employee, leave_application.leave_type)
            if allowed_balance < leave_days:
                messages.error(request, f'Insufficient balance! Allowable: {allowed_balance} days. Requested: {leave_days} days.')
                return redirect('core:leave_history')
            leave_application.save()
            messages.success(request, 'Leave application submitted successfully!')
            return redirect('core:leave_history')
    else:
        form = LeaveApplicationForm()

    return render(request, 'core/leave_management/apply_leave.html', {'form': form})



@login_required
def leave_history(request):
    leave_applications=[]
    leave_summary=[]
    employee=None
    try:
        user_profile = request.user.user_profile
        employee = Employee.objects.get(user_profile=user_profile)
        leave_applications = LeaveApplication.objects.filter(employee=employee).select_related('leave_type')
        leave_balances = EmployeeLeaveBalance.objects.filter(employee=employee).select_related('leave_type')

        approved_dict = {}
        for application in leave_applications:
            if application.leave_type.id in approved_dict:
                approved_dict[application.leave_type.id] += application.approved_no_of_days                
            else:
                approved_dict[application.leave_type.id] = application.approved_no_of_days               

        leave_summary = []
        for balance in leave_balances:
            leave_type = balance.leave_type
            total_leave = balance.balance
            approved_leave = approved_dict.get(leave_type.id, 0)  
            carry_forward = balance.carry_forward or 0
            available_leave = total_leave -  approved_leave if approved_leave else total_leave

            leave_summary.append({
                'leave_type': leave_type.name,
                'total_leave': total_leave,
                'approved_leave': approved_leave,
                'available_leave': available_leave,
                'employee': employee,
                'carry_forward': carry_forward
            })

    except Employee.DoesNotExist:
        messages.error(request, "No employee record found for your profile.")
       

    return render(request, 'core/leave_management/leave_history.html', {
        'leave_applications': leave_applications,  # Pass applications directly
        'leave_summary': leave_summary,
        'employee': employee,
    })




@login_required
def leave_summary(request):
    try:
        current_year = timezone.now().year
        user_profile = request.user.user_profile
        employee = Employee.objects.get(user_profile=user_profile)
        leave_balances = EmployeeLeaveBalance.objects.filter(employee=employee)     
        availed_leaves = LeaveApplication.objects.filter(
            employee=employee,
            status='APPROVED'  
        ).values('leave_type').annotate(total_availed=Sum('approved_no_of_days'))  

        availed_dict = {item['leave_type']: item['total_availed'] for item in availed_leaves}
      
        leave_summary = []
        for balance in leave_balances:
            leave_type = balance.leave_type
            total_leave = balance.balance  
            availed_leave = availed_dict.get(leave_type.id, 0)  
            available_leave = total_leave - availed_leave 
            carry_forward = balance.carry_forward

            leave_summary.append({
                'leave_type': leave_type.name,
                'total_leave': total_leave,
                'availed_leave': availed_leave,
                'available_leave': available_leave,
                'employee':employee,
                'carry_forward':carry_forward 
            })

    except Employee.DoesNotExist:
        messages.error(request, "No employee record found for your profile.")
        return redirect('core:dashboard')

    return render(request, 'core/leave_management/leave_summary.html', {
        'leave_summary': leave_summary,
        'employee':employee,
        'current_year': current_year
    })



@login_required
def approve_leave(request, leave_id):
    leave_application = get_object_or_404(LeaveApplication, id=leave_id)
    if not request.user.is_staff:
        messages.error(request, 'Unauthorized action!')
        return redirect('core:pending_leave_list')
    if request.method == 'POST':
        form = ApprovalForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['approved_start_date']
            end_date = form.cleaned_data['approved_end_date']

            leave_days = (end_date - start_date).days + 1

            if leave_application.status != 'APPROVED':
                balance_record = EmployeeLeaveBalance.objects.get(
                    employee=leave_application.employee,
                    leave_type=leave_application.leave_type,
                )

                allowed_balance = get_accrued_balance(leave_application.employee, leave_application.leave_type)
                if allowed_balance >= leave_days:
                    balance_record.balance -= leave_days
                    balance_record.save()

                    leave_application.status = 'APPROVED'
                    leave_application.approved_start_date = start_date
                    leave_application.approved_end_date = end_date
                    leave_application.approved_on = timezone.now()
                    leave_application.save()

                    messages.success(request, f'Leave approved for {leave_days} days.')
                else:
                    messages.error(
                        request,
                        f'Insufficient balance! Allowable: {allowed_balance} days. Requested: {leave_days} days.'
                    )
            else:
                messages.info(request, 'Leave is already approved.')
            return redirect('core:pending_leave_list')

        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        initial_days = (leave_application.applied_end_date - leave_application.applied_start_date).days + 1
        form = ApprovalForm(initial={
            'approved_start_date': leave_application.applied_start_date,
            'approved_end_date': leave_application.applied_end_date,
            'leave_type':leave_application.leave_type
        })

    return render(request, 'core/leave_management/approve_leave.html', {'form': form, 'leave_application': leave_application})


@login_required
def pending_leave_list(request):
    if not request.user.is_staff:
        messages.error(request, "Unauthorized access!")
        return redirect('core:leave_dashboard')

    pending_applications = LeaveApplication.objects.filter(status='PENDING')
  
    pending_with_balance = []
    for leave_application in pending_applications:
        allowed_balance = get_accrued_balance(leave_application.employee, leave_application.leave_type)

        pending_with_balance.append({
            'application': leave_application,
            'allowed_balance': allowed_balance
        })

    return render(request, 'core/leave_management/pending_leave_list.html', {
        'pending_with_balance': pending_with_balance
    })


################################## late in adjustment #################

from datetime import time
from.models import AttendanceModel
from django.http import JsonResponse
from.models import LeaveBalanceHistory

LATE_THRESHOLD = time(9, 30)  # Example: Late after 9:30 AM

def mark_late(attendance):
    if attendance.check_in_time and attendance.check_in_time > LATE_THRESHOLD:
        attendance.is_late = True
    else:
        attendance.is_late = False
    attendance.save()



def check_three_consecutive_lates(employee):
    today = date.today()
    recent_attendance = AttendanceModel.objects.filter(
        employee=employee, is_late=True
    ).order_by('-date')[:3]

    if len(recent_attendance) < 3:
        return False 
 
    dates = [att.date for att in recent_attendance]
    return dates[0] == today and dates[1] == today - timedelta(days=1) and dates[2] == today - timedelta(days=2)



def check_five_lates_in_month(employee):   
    today = date.today()
    month_start = today.replace(day=1)

    late_count = AttendanceModel.objects.filter(
        employee=employee,
        is_late=True,
        date__gte=month_start,
        date__lte=today
    ).count()

    return late_count >= 5


def deduct_earned_leave(employee):
    try:
        earned_leave_balance = EmployeeLeaveBalance.objects.get(
            employee=employee, leave_type__name='Earned Leave'
        )

        if earned_leave_balance.balance > 0:
            earned_leave_balance.balance -= 1
            earned_leave_balance.save()

            LeaveBalanceHistory.objects.create(
                employee=employee,
                leave_type=earned_leave_balance.leave_type,
                change=-1,
                reason='Deduction due to attendance lateness policy'
            )
            return True
    except EmployeeLeaveBalance.DoesNotExist:        
        pass
    return False



@login_required
def check_and_deduct_late_leaves(request):
    employees = Employee.objects.all()
    deductions = []

    for employee in employees:
        if check_three_consecutive_lates(employee) or check_five_lates_in_month(employee):
            deducted = deduct_earned_leave(employee)
            if deducted:
                deductions.append(f"Deducted 1 Earned Leave for {employee.name} due to lateness policy.")

    if deductions:
        messages.success(request, f"Deductions made: {', '.join(deductions)}")
        return JsonResponse({'status': 'success', 'deductions': deductions})
    else:
        messages.info(request, "No deductions were made today.")
    return redirect('core:leave_dashboard')

