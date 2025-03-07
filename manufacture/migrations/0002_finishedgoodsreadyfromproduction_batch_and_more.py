# Generated by Django 5.1.2 on 2025-02-25 14:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manufacture', '0001_initial'),
        ('purchase', '0003_batch_purchaseorderitem_batch'),
    ]

    operations = [
        migrations.AddField(
            model_name='finishedgoodsreadyfromproduction',
            name='batch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='batch_finished_goods', to='purchase.batch'),
        ),
        migrations.AddField(
            model_name='materialsdeliveryitem',
            name='batch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='batch_manufacture_delivery', to='purchase.batch'),
        ),
        migrations.AddField(
            model_name='materialsrequestitem',
            name='batch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='batch_manufacture', to='purchase.batch'),
        ),
    ]
