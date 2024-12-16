# Generated by Django 5.1.2 on 2024-12-16 07:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0012_alter_inventorytransaction_transaction_type'),
        ('repairreturn', '0003_alter_scrappeditem_scrapped_order_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventorytransaction',
            name='scrapped_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='scrapped_order_inventory', to='repairreturn.scrappedorder'),
        ),
    ]
