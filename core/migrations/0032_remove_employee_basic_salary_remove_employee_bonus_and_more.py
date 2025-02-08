# Generated by Django 5.1.2 on 2025-01-22 10:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_alter_position_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='basic_salary',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='bonus',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='car_entitle_status',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='gross_monthly_salary',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='house_allowance',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='medical_allowance',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='overtime_pay_rate',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='transportation_allowance',
        ),
        migrations.AddField(
            model_name='employee',
            name='loan_deductions',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, help_text='Deductions for any loans taken by the employee', max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='monthly_net_pay',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='other_deductions',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, help_text='Other miscellaneous deductions', max_digits=10, null=True),
        ),
        migrations.CreateModel(
            name='CompanyPolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('policy_code', models.CharField(max_length=30)),
                ('hra_percentage', models.DecimalField(decimal_places=2, default=40.0, max_digits=5)),
                ('medical_allowance_percentage', models.DecimalField(decimal_places=2, default=10.0, max_digits=5)),
                ('conveyance_allowance_percentage', models.DecimalField(decimal_places=2, default=5.0, max_digits=5)),
                ('performance_bonus_percentage', models.DecimalField(decimal_places=2, default=5.0, max_digits=5)),
                ('festival_bonus_percentage', models.DecimalField(decimal_places=2, default=5.0, max_digits=5)),
                ('provident_fund_percentage', models.DecimalField(decimal_places=2, default=12.0, max_digits=5)),
                ('grauity_percentage', models.DecimalField(decimal_places=2, default=12.0, max_digits=5)),
                ('leave_travel_allowance_performance', models.DecimalField(decimal_places=2, default=12.0, max_digits=5)),
                ('professional_tax', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.company')),
            ],
        ),
        migrations.CreateModel(
            name='SalaryStructure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('salary_structure_code', models.CharField(max_length=50)),
                ('salary_level', models.CharField(choices=[('LEVEL-1', 'Level-1'), ('LEVEL2', 'Level-2'), ('LEVEL-3', 'Level-3'), ('LEVEL-4', 'Level-4'), ('LEVEL-5', 'Level-5'), ('LEVEL-6', 'Level-6'), ('LEVEL-7', 'Level-7'), ('LEVEL-8', 'Level-8'), ('LEVEL-9', 'Level-9'), ('LEVEL-10', 'Level-10')], max_length=50)),
                ('basic_salary', models.DecimalField(decimal_places=2, help_text='Base salary of the employee', max_digits=15)),
                ('car_entitle_status', models.BooleanField(default=False, verbose_name='Entitled to a car?')),
                ('food_allowance', models.DecimalField(decimal_places=2, default=0.0, help_text='Allowance for meals or food', max_digits=10)),
                ('insurance', models.BooleanField(default=False, verbose_name='Cover insurance policy?')),
                ('stock_options', models.BooleanField(default=False, verbose_name='have stock option?')),
                ('income_tax_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Income tax deduction', max_digits=10)),
                ('overtime_pay_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Rate per hour for overtime work', max_digits=10)),
                ('income_tax_percentage', models.DecimalField(decimal_places=2, default=0.0, help_text='Income tax deduction', max_digits=10)),
                ('company_policy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.companypolicy')),
            ],
        ),
        migrations.AddField(
            model_name='employee',
            name='salary_structure',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.salarystructure'),
        ),
    ]
