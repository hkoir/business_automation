
from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from accounts.models import UserProfile
from decimal import Decimal
from django.utils import timezone
from datetime import datetime
from core.utils import DEPARTMENT_CHOICES,EMPLOYEE_LEVEL_CHOICES,POSITION_CHOICES,LOCATION_CHOICES
import uuid


class Notice(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255,null=True,blank=True)
    content = models.TextField(null=True,blank=True)
    notice_attachment = models.ImageField(upload_to='notices',null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Department(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100,choices=DEPARTMENT_CHOICES)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Position(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100,choices=POSITION_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="positions")
    description = models.TextField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'department'], name='unique_position_in_department')
        ]

    def __str__(self):
        return self.name


class Company(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='company_hq_user')
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='company_logo/',blank=True, null=True)
    contact_person = models.CharField(max_length=30,null=True,blank=True)
    website = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return self.name


class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='company_location_user')
    company = models.ForeignKey(Company, related_name='company_locations', on_delete=models.CASCADE,null=True, blank=True)
    name = models.CharField(max_length=255,null=True, blank=True,choices=LOCATION_CHOICES)
       
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



class Employee(models.Model):   
    user_profile = models.ForeignKey(UserProfile,on_delete=models.CASCADE,null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True,default="Nome")    
    first_name = models.CharField(max_length=100, null=True, blank=True,default="Nome")
    last_name = models.CharField(max_length=100,null=True, blank=True,default="Nome")  
   
    location = models.ForeignKey(Location,on_delete=models.SET_NULL,null=True,blank=True)
    position = models.ForeignKey(Position,on_delete=models.CASCADE,null=True, blank=True)
    department = models.ForeignKey(Department,on_delete=models.CASCADE,null=True, blank=True)            
    employe_level= models.CharField(max_length=100, choices=EMPLOYEE_LEVEL_CHOICES, default='executive',null=True, blank=True)
    employee_code = models.CharField(max_length=100, null=True, blank=True)
   
    gender_choices =[
        ('Male','Male'),
        ('Female','Female'),
        ('Others', 'Others')
    ]
    gender = models.CharField(max_length=20,choices= gender_choices,null=True, blank=True,default="Nome")
    joining_date = models.DateField(null=True,blank=True)
    resignation_date = models.DateField(null=True, blank=True, default=timezone.now, help_text="Format: YYYY-MM-DD")
      
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True,default=0.00)
    car_entitle_status = models.BooleanField(default=False)
    house_allowance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,default=0.00)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True, default=0.00)
    transportation_allowance = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True, default=0.00)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    overtime_pay_rate = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True, default=0.00)
    employee_photo_ID = models.ImageField(upload_to='employee_photo_ID/', null=True, blank=True)
    gross_monthly_salary = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True, default=0.00)
    
    promotion_status = models.BooleanField(db_default=False)
    incremental_status = models.BooleanField(default=False)   

    created_at=models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.employee_code or self.employee_code == 'None':
            self.employee_code = f"EMP-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

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




class EmployeeRecordChange(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(default=timezone.now)
    field_name = models.CharField(max_length=100,default="None")
    old_value = models.CharField(max_length=255, default="None")
    new_value = models.CharField(max_length=255,default="None" )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class AttendanceModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


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
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    month = models.IntegerField()  # Month number (e.g., 1 for January)
    year = models.IntegerField()
    total_working_hours = models.DecimalField(max_digits=5, decimal_places=2 , null=True, blank=True )
    total_salary = models.DecimalField(max_digits=10, decimal_places=2 , null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



