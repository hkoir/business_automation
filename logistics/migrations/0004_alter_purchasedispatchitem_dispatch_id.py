# Generated by Django 5.1.2 on 2024-11-08 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0003_alter_purchasedispatchitem_dispatch_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchasedispatchitem',
            name='dispatch_id',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
