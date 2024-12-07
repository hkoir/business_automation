
from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from accounts.models import UserProfile
from decimal import Decimal
from django.utils import timezone
from datetime import datetime




class Notice(models.Model):
    title = models.CharField(max_length=255,null=True,blank=True)
    content = models.TextField(null=True,blank=True)
    notice_attachment = models.ImageField(upload_to='notices',null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title




class Employee(models.Model):    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='employee_user')
    user_profile = models.ForeignKey(UserProfile,on_delete=models.CASCADE,null=True, blank=True)
    employee_code = models.CharField(max_length=100, unique=True, null=True, blank=True, default='None')
    name = models.CharField(max_length=100, null=True, blank=True,default="Nome")
    first_name = models.CharField(max_length=100, null=True, blank=True,default="Nome")
    last_name = models.CharField(max_length=100,null=True, blank=True,default="Nome")
    posting_area_choices=[
        ('Dhaka','Dhaka'),
        ('Rangpur','Rangpur'),
        ('Sylhet','Sylhet'),
        ('Rajshahi','Rajshahi'),
        ('Chittagong','Chittagong')
    ]
    posting_area = models.CharField(max_length=100,choices=posting_area_choices,null=True,blank=True)

    gender_choices =[
        ('Male','Male'),
        ('Female','Female'),
        ('Others', 'Others')
    ]
    gender = models.CharField(max_length=20,choices= gender_choices,null=True, blank=True,default="Nome")
    joining_date = models.DateField(null=True,blank=True)
    resignation_date = models.DateField(null=True, blank=True, default=timezone.now, help_text="Format: YYYY-MM-DD")

    position_choices=[

        ('Chairman','Chairman'),
        ('MD','MD'),
        ('CEO','CEO'),
        ('CFO','CFO'),
        ('CMO','CMO'),
        ('CTO','CTO'),
        ('Specialist','Specialist'),
        ('Manager','Manager'),
        ('Sr.Manager','Sr.Manager'),
        ('DGM','DGM'),
        ('GM','GM'),
        ('SrGM','SrGM'),
        ('Director','Director'),
        ('HOD','HOD'),
        ('Specialist','Specialist'),

        ('HSS_manager','HSS_manager'),
        ('Driver','Driver'),
        ('Peon','Peon'),
        ('General staff','General staff'),
     

        
    ]
    position = models.CharField(max_length=100,null=True, blank=True,choices= position_choices,default="Nome")

    department_choices=[

        ('Engineering','Engineering'),
        ('Marketting','Marketing'),
        ('Finance','Finance'),
        ('Accounting','Accounting'),
        ('Technology','Technology'),
        ('Admin','Admin'),
        ('HR','HR'),
        ('Business_Development','Business_Development'),
        
    ]
    department = models.CharField(max_length=100,null=True, blank=True,choices=department_choices,default="Nome")
    
    
    employee_level_choices=[
        ('SeniorManagement','SeniorManagement'),
        ('MidLevelManager','MidLevelManager'),
        ('FirstLevelmanager','FirstLevelManager'),
        ('Executive','Executive'),
        ('Engineer','Engineer'),
        ('Doctor','Doctor'),
        ('Specialist','Specialist'),
        ('Officer','Officer'),
        ('FieldForce','FieldForce'),
        ('General_Staffs','General_Staffs'),
    ]
    employe_level= models.CharField(max_length=100, choices=employee_level_choices, default='executive',null=True, blank=True)
   
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True,default=0.00)
    house_allowance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,default=0.00)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True, default=0.00)
    transportation_allowance = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True, default=0.00)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    overtime_pay_rate = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True, default=0.00)
    employee_photo_ID = models.ImageField(upload_to='employee_photo_ID/', null=True, blank=True)
    gross_monthly_salary = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True, default=0.00)
    created_at=models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
  

    def save(self, *args, **kwargs):

        percentage_40 = Decimal('0.4')
        percentage_30 = Decimal('0.3')
        self.house_allowance = self.basic_salary * percentage_40
        self.medical_allowance = self.basic_salary * percentage_40
        self.transportation_allowance = self.basic_salary * percentage_30
        self.bonus = self.basic_salary * percentage_40
        self. gross_monthly_salary = self.basic_salary + self.house_allowance + self.medical_allowance + self.transportation_allowance
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name



class Company(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='company_hq_user')
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='company_logo/',blank=True, null=True)
    contact_person = models.ForeignKey(Employee,on_delete=models.CASCADE,related_name='hq_employee_name')
    website = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return self.name


class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='company_location_user')
    company = models.ForeignKey(Company, related_name='company_locations', on_delete=models.CASCADE,null=True, blank=True)
    name = models.CharField(max_length=255,null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=20,null=True, blank=True)
    email = models.EmailField(null=True, blank=True)    
    city = models.CharField(max_length=100,null=True,blank=True)
    state = models.CharField(max_length=100,null=True,blank=True)
    country = models.CharField(max_length=100,null=True,blank=True)
    postal_code = models.CharField(max_length=20,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        app_label = 'core'

    def __str__(self):
        return f"{self.name}"



class EmployeeRecordChange(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(default=timezone.now)
    field_name = models.CharField(max_length=100,default="None")
    old_value = models.CharField(max_length=255, default="None")
    new_value = models.CharField(max_length=255,default="None" )



class AttendanceModel(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    check_in_time = models.TimeField()
    check_out_time = models.TimeField(null=True, blank=True)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.00)
    
    attendance_status_choices=[
        ('present', 'present'),
        ('absent', 'absent'),

    ]
    attendance_status= models.CharField(max_length=50,choices= attendance_status_choices,default='None')
   
    def calculate_total_hours(self):
        if self.check_out_time and self.check_in_time:
            check_in = datetime.combine(datetime.min, self.check_in_time)
            check_out = datetime.combine(datetime.min, self.check_out_time)
            duration = check_out - check_in
            total_hours = duration.total_seconds() / 3600  # Convert seconds to hours
            return round(total_hours, 2)
        else:
            return 0.0  # Return 0.0 if either check_in_time or check_out_time is None

    def save(self, *args, **kwargs):
        self.total_hours = self.calculate_total_hours()
        super().save(*args, **kwargs)
   

    def __str__(self):
        return f"{self.employee} - {self.date}"
    



class MonthlySalaryReport(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    month = models.IntegerField()  # Month number (e.g., 1 for January)
    year = models.IntegerField()
    total_working_hours = models.DecimalField(max_digits=5, decimal_places=2 , null=True, blank=True )
    total_salary = models.DecimalField(max_digits=10, decimal_places=2 , null=True, blank=True)




