# Generated by Django 5.1.2 on 2025-02-25 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0003_batch_purchaseorderitem_batch'),
    ]

    operations = [
        migrations.AddField(
            model_name='batch',
            name='remaining_quantity',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
