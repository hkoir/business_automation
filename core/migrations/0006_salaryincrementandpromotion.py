# Generated by Django 5.1.2 on 2024-12-27 08:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_employee_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalaryIncrementAndPromotion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('increment_year', models.IntegerField(blank=True, null=True)),
                ('increment_section', models.CharField(blank=True, choices=[('BY_EMPLOYEE', 'By Employee'), ('BY_DEPARTMENT', 'By department'), ('BY_COMPANY', 'By Company')], max_length=30, null=True)),
                ('increment_type', models.CharField(blank=True, choices=[('MONTHLY', 'Monthly'), ('QUARTERLY', 'Quarterly'), ('HALF_YEARLY', 'Half Yearly'), ('YEARLY', 'Yearly')], max_length=30, null=True)),
                ('month', models.CharField(blank=True, choices=[('JANUARY', 'January'), ('FEBRUARY', 'February'), ('MARCH', 'March'), ('APRIL', 'April'), ('MAY', 'May'), ('JUNE', 'June'), ('JULY', 'July'), ('AUGUST', 'August'), ('SEPTEMBER', 'September'), ('OCTOBER', 'October'), ('NOVEMBER', 'November'), ('DECEMBER', 'December')], max_length=30, null=True)),
                ('quarter', models.CharField(blank=True, choices=[('1ST_QUARTER', '1st Quarter'), ('2ND_QUARTER', '2nd Quarter'), ('3RD_QUARTER', '3rd Quarter'), ('4TH_QUARTER', '4th Quarter')], max_length=30, null=True)),
                ('half_year', models.CharField(blank=True, choices=[('FIRST_HALF_YEAR', 'First Half Year'), ('SECOND_HALF_YEAR', 'Second Half Year')], max_length=30, null=True)),
                ('increment_percentage', models.FloatField(blank=True, null=True)),
                ('increment_amount', models.FloatField(blank=True, null=True)),
                ('new_salary', models.FloatField(blank=True, null=True)),
                ('obtained_promotion_recommendation', models.CharField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No')], max_length=10, null=True)),
                ('given_promotion_recommendation', models.CharField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No')], max_length=10, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='increment_department', to='core.department')),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='increment_history', to='core.employee')),
            ],
        ),
    ]
