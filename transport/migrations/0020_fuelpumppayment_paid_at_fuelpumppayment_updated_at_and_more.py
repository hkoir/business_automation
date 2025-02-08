# Generated by Django 5.1.2 on 2025-01-17 02:09

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0019_fuelpumppayment'),
    ]

    operations = [
        migrations.AddField(
            model_name='fuelpumppayment',
            name='paid_at',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='fuelpumppayment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='fuelrefill',
            name='paid_at',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='fuelrefill',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='vehiclerentalcost',
            name='paid_at',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='vehiclerentalcost',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='fuelpumppayment',
            name='created_at',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='fuelrefill',
            name='created_at',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='vehiclerentalcost',
            name='created_at',
            field=models.DateField(auto_now_add=True),
        ),
    ]
