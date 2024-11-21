# Generated by Django 5.1.2 on 2024-11-08 12:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inventory', '0001_initial'),
        ('manufacture', '0001_initial'),
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalinventorytransaction',
            name='manufacture_order',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='manufacture.receivefinishedgoods'),
        ),
        migrations.AddField(
            model_name='historicalinventorytransaction',
            name='product',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='product.product'),
        ),
    ]
