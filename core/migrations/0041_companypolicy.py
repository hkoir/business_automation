# Generated by Django 5.1.2 on 2025-01-22 18:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_remove_salarystructure_company_policy_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyPolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('policy_code', models.CharField(blank=True, max_length=30, null=True)),
                ('hra_percentage', models.DecimalField(blank=True, decimal_places=2, default=40.0, max_digits=5, null=True)),
                ('medical_allowance_percentage', models.DecimalField(blank=True, decimal_places=2, default=10.0, max_digits=5, null=True)),
                ('conveyance_allowance_percentage', models.DecimalField(blank=True, decimal_places=2, default=5.0, max_digits=5, null=True)),
                ('performance_bonus_percentage', models.DecimalField(blank=True, decimal_places=2, default=5.0, max_digits=5, null=True)),
                ('festival_bonus_percentage', models.DecimalField(blank=True, decimal_places=2, default=5.0, max_digits=5, null=True)),
                ('provident_fund_percentage', models.DecimalField(blank=True, decimal_places=2, default=12.0, max_digits=5, null=True)),
                ('professional_tax', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True)),
                ('grauity_percentage', models.DecimalField(blank=True, decimal_places=2, default=12.0, max_digits=5, null=True)),
                ('leave_travel_allowance_performance', models.DecimalField(blank=True, decimal_places=2, default=12.0, max_digits=5, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.company')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
