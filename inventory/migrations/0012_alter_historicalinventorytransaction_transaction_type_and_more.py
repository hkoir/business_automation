# Generated by Django 5.1.2 on 2024-11-20 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0011_alter_historicalinventorytransaction_transaction_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalinventorytransaction',
            name='transaction_type',
            field=models.CharField(blank=True, choices=[('INBOUND', 'Inbound'), ('OUTBOUND', 'Outbound'), ('MANUFACTURE', 'Manufacture'), ('REPLACEMENT_OUT', 'Replacement Out'), ('REPLACEMENT_IN', 'Replacement In'), ('TRANSFER_OUT', 'Transfer Out'), ('TRANSFER_IN', 'Transfer In')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='inventorytransaction',
            name='transaction_type',
            field=models.CharField(blank=True, choices=[('INBOUND', 'Inbound'), ('OUTBOUND', 'Outbound'), ('MANUFACTURE', 'Manufacture'), ('REPLACEMENT_OUT', 'Replacement Out'), ('REPLACEMENT_IN', 'Replacement In'), ('TRANSFER_OUT', 'Transfer Out'), ('TRANSFER_IN', 'Transfer In')], max_length=20, null=True),
        ),
    ]
