# Generated by Django 5.1.2 on 2025-01-14 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0007_remove_transportusage_end_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transportusage',
            name='end_datetime',
        ),
        migrations.RemoveField(
            model_name='transportusage',
            name='start_datetime',
        ),
        migrations.AddField(
            model_name='transport',
            name='vehicle_fuel_unit_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AddField(
            model_name='transportusage',
            name='end_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='transportusage',
            name='start_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
