from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Employee
from core.forms import AddEmployeeForm
import uuid
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from.models import Location,Company
from.forms import AddCompanyForm,AddLocationForm,UpdateLocationForm





def home(request):
    return render(request,'core/home.html')

def core_dashboard(request):
    return render(request,'core/core_dashboard.html')



@login_required
def view_employee(request):
    employee_records = Employee.objects.all()
    paginator = Paginator(employee_records, 10) 
    page_number = request.GET.get('page')
    try:
        employee_records = paginator.page(page_number)
    except PageNotAnInteger:
        employee_records = paginator.page(1)
    except EmptyPage:
       employee_records = paginator.page(paginator.num_pages)
    return render(request, 'core/view_employee.html', {'employee_records': employee_records})




def add_employee(request):
    if request.method == 'POST':   
        form = AddEmployeeForm(request.POST, request.FILES)
        if form.is_valid():      
            form.instance.employee_code = f"EID-{uuid.uuid4().hex[:8].upper()}"
            form.save()
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
            form.save()
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
        form.save()
        messages.success(request, message_text)
        return redirect('core:view_employee')

    datas = Employee.objects.all()
    paginator = Paginator(datas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/manage_employee.html', {
        'form': form,
        'instance': instance,
        'datas': datas,
        'page_obj': page_obj
    })


def employee_list(request):
    employees = Employee.objects.all()
    return render(request,'core/employee/employee_list.html', {'employees': employees})





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




def manage_location(request, id=None):
    if request.method == 'POST' and 'delete_id' in request.POST:
        instance = get_object_or_404(Location, id=request.POST.get('delete_id'))
        instance.delete()
        messages.success(request, "Deleted successfully")
        return redirect('core:create_location')

    instance = get_object_or_404(Location, id=id) if id else None
    message_text = "updated successfully!" if id else "added successfully!"
    form = AddLocationForm(request.POST or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, message_text)
        return redirect('core:create_location')

    datas = Location.objects.all().order_by('-created_at')
    paginator = Paginator(datas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/manage_location.html', {
        'form': form,
        'instance': instance,
        'datas': datas,
        'page_obj': page_obj
    })


from .models import EmployeeRecordChange,MonthlySalaryReport,AttendanceModel
from openpyxl import Workbook
from io import BytesIO
from django.http import HttpResponse

@login_required
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
    return render(request, 'core/employee/employee_change_record.html', {'changes': changes})


@login_required
def view_employee_changes_single(request, employee_id): 
    employee = get_object_or_404(Employee, pk=employee_id)
    changes_single = EmployeeRecordChange.objects.filter(employee=employee)
    return render(request, 'core/employee/employee_change_record.html', {'changes_single': changes_single})

from.forms import EditAttendanceForm,MonthYearForm,AttendanceForm



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
    return render(request, 'core/employee/attendance_form.html', {'form': form})


@login_required
def view_attendance(request):
    attendance_records = AttendanceModel.objects.all()
    return render(request, 'core/employee/view_attendance.html', {'attendance_records': attendance_records})


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
    return render(request, 'core/employee/attendance_form.html', {'form': form,'employee':employee})



month =None
year = None
@login_required
def create_salary(request):
    global month, year      
    if 'month' in request.GET:
        month = int(request.GET['month'])    
    if 'year' in request.GET:
        year = int(request.GET['year']) 
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
        return redirect('core:create_salary')
    else:
        form = MonthYearForm()      
    salary = MonthlySalaryReport.objects.filter(month = month, year =year)
    context = {'form': form, 'salary': salary,'month':month, 'year':year}
    return render(request, 'core/employee/create_monthly_salary.html', context)



def generate_salary_sheet(month, year):  
    salary_reports = MonthlySalaryReport.objects.filter(month=month, year=year)
    salary_sheet = []  
    for report in salary_reports:
        employee = report.employee
        total_salary = report.total_salary
        salary_sheet.append({'employee': employee, 'total_salary': total_salary})
    return salary_sheet


@login_required
def download_salary(request):
    global month,year
    salary_sheet = generate_salary_sheet(month, year)  
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Salary Report'  
    headers = ['Employee ID', 'Name', 'Total Salary']
    worksheet.append(headers)
    for entry in salary_sheet:
        row = [entry['employee'].employee_code, entry['employee'].name, entry['total_salary']]
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



from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4,letter
from reportlab.pdfgen import canvas
from django.utils import timezone


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
    cfo_employee = Employee.objects.filter(position='CFO').first()
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

import os
from django.conf import settings
from datetime import datetime

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
    cfo_employee = Employee.objects.filter(position='CFO').first()
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
    cfo_employee = Employee.objects.filter(position='CFO').first()
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




from.forms import NoticeForm
from.models import Notice



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