# Generated by Django 5.1.2 on 2025-01-13 14:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transport',
            name='vehicle_fuel_unit_price',
        ),
    ]
