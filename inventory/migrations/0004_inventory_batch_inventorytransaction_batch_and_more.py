# Generated by Django 5.1.2 on 2025-02-25 14:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_initial'),
        ('purchase', '0003_batch_purchaseorderitem_batch'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory',
            name='batch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='batch_inventory', to='purchase.batch'),
        ),
        migrations.AddField(
            model_name='inventorytransaction',
            name='batch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='batch_inventory_transaction', to='purchase.batch'),
        ),
        migrations.AddField(
            model_name='inventorytransaction',
            name='unit_cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='transferitem',
            name='batch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='batch_transfer', to='purchase.batch'),
        ),
    ]
