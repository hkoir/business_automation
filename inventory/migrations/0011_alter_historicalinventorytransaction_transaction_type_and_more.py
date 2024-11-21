# Generated by Django 5.1.2 on 2024-11-20 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_alter_historicalinventorytransaction_manufacture_order_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalinventorytransaction',
            name='transaction_type',
            field=models.CharField(blank=True, choices=[('INBOUND', 'Inbound'), ('OUTBOUND', 'Outbound'), ('MANUFACTURE', 'Manufacture'), ('REPLACEMENT_OUT', 'Replacement Out'), ('REPLACEMENT_IN', 'Replacement IN'), ('TRANSFER_OUT', 'Transfer Out'), ('TRANSFER_IN', 'Transfer IN')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='inventorytransaction',
            name='transaction_type',
            field=models.CharField(blank=True, choices=[('INBOUND', 'Inbound'), ('OUTBOUND', 'Outbound'), ('MANUFACTURE', 'Manufacture'), ('REPLACEMENT_OUT', 'Replacement Out'), ('REPLACEMENT_IN', 'Replacement IN'), ('TRANSFER_OUT', 'Transfer Out'), ('TRANSFER_IN', 'Transfer IN')], max_length=20, null=True),
        ),
    ]
