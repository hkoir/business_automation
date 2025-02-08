# Generated by Django 5.1.2 on 2025-01-04 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(blank=True, choices=[('PURCHASE-NOTIFICATION', 'Purchase notification'), ('SALES-NOTIFICATION', 'Sales Notification'), ('PRODUCTION-NOTIFICATION', 'Production notification')], max_length=50, null=True),
        ),
    ]
