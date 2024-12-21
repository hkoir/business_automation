# Generated by Django 5.1.2 on 2024-12-18 16:16

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='company_logo/')),
                ('contact_person', models.CharField(blank=True, max_length=30, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='company_hq_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('', ''), ('Engineering', 'Engineering'), ('Technology', 'Technology'), ('Operations', 'Operations'), ('Planning', 'Planning'), ('Information Technology', 'Information Technology'), ('Customer Support', 'Customer Support'), ('Research & Development', 'Research & Development'), ('Legal & Compliance', 'Legal & Compliance'), ('SCM', 'Supply Chain Management (SCM)'), ('Logistics', 'Logistics'), ('Quality Assurance', 'Quality Assurance'), ('Business Control', 'Business Control'), ('Design and Creative', 'Design and Creative'), ('Public Relations', 'Public Relations'), ('Corporate Strategy and Planning', 'Corporate Strategy and Planning'), ('Marketing', 'Marketing'), ('Sales', 'Sales'), ('Finance', 'Finance'), ('Accounting', 'Accounting'), ('Production', 'Production'), ('Admin', 'Admin'), ('HR', 'Human Resources'), ('Training and Development', 'Training and Development'), ('Event Management', 'Event Management'), ('Environmental, Social, and Governance (ESG)', 'Environmental, Social, and Governance (ESG)'), ('Health and Safety', 'Health and Safety'), ('Business Development', 'Business Development'), ('Facilities Management', 'Facilities Management'), ('Investor Relations', 'Investor Relations'), ('Medical Healthcare', 'Medical Healthcare'), ('Procurement', 'Procurement'), ('Security', 'Security'), ('Learning and Development', 'Learning and Development'), ('Corporate Communications', 'Corporate Communications'), ('Sustainability', 'Sustainability')], max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='Nome', max_length=100, null=True)),
                ('first_name', models.CharField(blank=True, default='Nome', max_length=100, null=True)),
                ('last_name', models.CharField(blank=True, default='Nome', max_length=100, null=True)),
                ('employe_level', models.CharField(blank=True, choices=[('', ''), ('Executive Leadership', 'Executive Leadership'), ('Senior Management', 'Senior Management'), ('Middle Management', 'Middle Management'), ('First-Line Management', 'First-Line Management'), ('Executive', 'Executive'), ('Senior Engineer', 'Senior Engineer'), ('Engineer', 'Engineer'), ('Junior Engineer', 'Junior Engineer'), ('Doctor', 'Doctor'), ('Specialist', 'Specialist'), ('Officer', 'Officer'), ('Field Force', 'Field Force'), ('General Staff', 'General Staff'), ('Intern', 'Intern'), ('Consultant', 'Consultant'), ('Technician', 'Technician'), ('Supervisor', 'Supervisor'), ('Associate', 'Associate')], default='executive', max_length=100, null=True)),
                ('employee_code', models.CharField(blank=True, default='None', max_length=100, null=True)),
                ('gender', models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others')], default='Nome', max_length=20, null=True)),
                ('joining_date', models.DateField(blank=True, null=True)),
                ('resignation_date', models.DateField(blank=True, default=django.utils.timezone.now, help_text='Format: YYYY-MM-DD', null=True)),
                ('basic_salary', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True)),
                ('car_entitle_status', models.BooleanField(default=False)),
                ('house_allowance', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True)),
                ('medical_allowance', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True)),
                ('transportation_allowance', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True)),
                ('bonus', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('overtime_pay_rate', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True)),
                ('employee_photo_ID', models.ImageField(blank=True, null=True, upload_to='employee_photo_ID/')),
                ('gross_monthly_salary', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True)),
                ('promotion_status', models.BooleanField(db_default=False)),
                ('incremental_status', models.BooleanField(default=False)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('department', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.department')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_user', to=settings.AUTH_USER_MODEL)),
                ('user_profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='AttendanceModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('check_in_time', models.TimeField()),
                ('check_out_time', models.TimeField(blank=True, null=True)),
                ('total_hours', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=5, null=True)),
                ('attendance_status', models.CharField(choices=[('present', 'present'), ('absent', 'absent')], default='None', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.employee')),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeRecordChange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changed_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('field_name', models.CharField(default='None', max_length=100)),
                ('old_value', models.CharField(default='None', max_length=255)),
                ('new_value', models.CharField(default='None', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.employee')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, choices=[('', ''), ('DHAKA', 'Dhaka'), ('CHITTAGONG', 'Chittagong'), ('KHULNA', 'Khulna'), ('RAJSHAHI', 'Rajshahi'), ('SYLHET', 'Sylhet'), ('BAGURA', 'Bagura'), ('BARISAL', 'Barisal'), ('MYMENSINGH', 'Mymensingh'), ('Cumilla', 'Cumilla')], max_length=255, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, max_length=100, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('postal_code', models.CharField(blank=True, max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='company_locations', to='core.company')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='company_location_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='employee',
            name='location',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.location'),
        ),
        migrations.CreateModel(
            name='MonthlySalaryReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.IntegerField()),
                ('year', models.IntegerField()),
                ('total_working_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('total_salary', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.employee')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('content', models.TextField(blank=True, null=True)),
                ('notice_attachment', models.ImageField(blank=True, null=True, upload_to='notices')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('', ''), ('Chairman', 'Chairman'), ('MD', 'MD'), ('CEO', 'CEO'), ('CFO', 'CFO'), ('COO', 'COO'), ('CTO', 'CTO'), ('CIO', 'CIO'), ('CHRO', 'CHRO'), ('CMO', 'CMO'), ('CSO', 'CSO'), ('CLO', 'CLO'), ('CDO', 'CDO'), ('Director', 'Director'), ('Executive Director', 'Executive Director'), ('HOD', 'HOD'), ('AVP', 'AVP'), ('VP', 'VP'), ('Senior VP', 'Senior VP'), ('General Manager', 'General Manager'), ('DGM', 'DGM'), ('GM', 'GM'), ('SrGM', 'SrGM'), ('Manager', 'Manager'), ('Sr.Manager', 'Sr.Manager'), ('Assistant Manager', 'Assistant Manager'), ('Team Lead', 'Team Lead'), ('Supervisor', 'Supervisor'), ('Coordinator', 'Coordinator'), ('HSS_manager', 'HSS_manager'), ('Specialist', 'Specialist'), ('Senior Specialist', 'Senior Specialist'), ('Officer', 'Officer'), ('Executive Officer', 'Executive Officer'), ('Project Manager', 'Project Manager'), ('Program Manager', 'Program Manager'), ('Consultant', 'Consultant'), ('Advisor', 'Advisor'), ('Engineer', 'Engineer'), ('Senior Engineer', 'Senior Engineer'), ('Software Developer', 'Software Developer'), ('System Analyst', 'System Analyst'), ('Data Scientist', 'Data Scientist'), ('IT Specialist', 'IT Specialist'), ('Architect', 'Architect'), ('Driver', 'Driver'), ('Peon', 'Peon'), ('Office Assistant', 'Office Assistant'), ('Receptionist', 'Receptionist'), ('Clerk', 'Clerk'), ('Secretary', 'Secretary'), ('General Staff', 'General Staff'), ('Personal Assistant', 'Personal Assistant'), ('Administrative Officer', 'Administrative Officer'), ('Sales Manager', 'Sales Manager'), ('Sales Executive', 'Sales Executive'), ('Marketing Manager', 'Marketing Manager'), ('Marketing Executive', 'Marketing Executive'), ('Business Development Manager', 'Business Development Manager'), ('Account Manager', 'Account Manager'), ('HR Manager', 'HR Manager'), ('HR Executive', 'HR Executive'), ('Recruiter', 'Recruiter'), ('Training Manager', 'Training Manager'), ('Payroll Specialist', 'Payroll Specialist'), ('Finance Manager', 'Finance Manager'), ('Accountant', 'Accountant'), ('Auditor', 'Auditor'), ('Legal Advisor', 'Legal Advisor'), ('Compliance Officer', 'Compliance Officer'), ('Operations Manager', 'Operations Manager'), ('Logistics Manager', 'Logistics Manager'), ('Warehouse Supervisor', 'Warehouse Supervisor'), ('Procurement Officer', 'Procurement Officer'), ('Inventory Manager', 'Inventory Manager'), ('Research Scientist', 'Research Scientist'), ('R&D Manager', 'R&D Manager'), ('Product Developer', 'Product Developer'), ('Teacher', 'Teacher'), ('Lecturer', 'Lecturer'), ('Professor', 'Professor'), ('Trainer', 'Trainer'), ('Coach', 'Coach'), ('Doctor', 'Doctor'), ('Nurse', 'Nurse'), ('Pharmacist', 'Pharmacist'), ('Lab Technician', 'Lab Technician'), ('Medical Assistant', 'Medical Assistant'), ('Volunteer', 'Volunteer'), ('Intern', 'Intern'), ('Trainee', 'Trainee')], max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='positions', to='core.department')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='employee',
            name='position',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.position'),
        ),
        migrations.AddConstraint(
            model_name='position',
            constraint=models.UniqueConstraint(fields=('name', 'department'), name='unique_position_in_department'),
        ),
    ]
