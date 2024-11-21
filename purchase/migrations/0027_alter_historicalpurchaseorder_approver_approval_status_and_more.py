# Generated by Django 5.1.2 on 2024-11-16 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0026_historicalpurchaseorder_approver_approval_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpurchaseorder',
            name='approver_approval_status',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='historicalpurchaseorder',
            name='requester_approval_status',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='historicalpurchaseorder',
            name='reviewer_approval_status',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='approver_approval_status',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='requester_approval_status',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='reviewer_approval_status',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
