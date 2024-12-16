# Generated by Django 5.1.2 on 2024-12-14 09:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0008_remove_inventory_inventory_transaction_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventorytransaction',
            name='inventory',
        ),
        migrations.AddField(
            model_name='inventory',
            name='inventory_transaction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.inventorytransaction'),
        ),
    ]
