# Generated by Django 5.1.2 on 2024-12-26 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0004_alter_saledispatchitem_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='saledispatchitem',
            name='status',
            field=models.CharField(blank=True, choices=[('IN_PROCESS', 'In Process'), ('READY_FOR_QC', 'Ready for QC'), ('DISPATCHED', 'Dispatched'), ('ON_BOARD', 'On Board'), ('IN_TRANSIT', 'In Transit'), ('CUSTOM_CLEARANCE_IN_PROCESS', 'Custom Clearance In Process'), ('REACHED', 'Reached'), ('OBI', 'OBI done'), ('DELIVERED', 'Delivered'), ('CANCELLED', 'Cancelled')], default='IN_PROCESS', max_length=30, null=True),
        ),
    ]
