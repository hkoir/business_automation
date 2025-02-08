# Generated by Django 5.1.2 on 2025-01-22 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_alter_companypolicy_conveyance_allowance_percentage_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salarystructure',
            name='company_policy',
        ),
        migrations.RemoveField(
            model_name='salarystructure',
            name='user',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='salary_structure',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='loan_deductions',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='monthly_net_pay',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='other_deductions',
        ),
        migrations.AddField(
            model_name='employee',
            name='basic_salary',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='bonus',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='employee',
            name='gross_monthly_salary',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='house_allowance',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='medical_allowance',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='overtime_pay_rate',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pictures/'),
        ),
        migrations.AddField(
            model_name='employee',
            name='transportation_allowance',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True),
        ),
        migrations.DeleteModel(
            name='CompanyPolicy',
        ),
        migrations.DeleteModel(
            name='SalaryStructure',
        ),
    ]
