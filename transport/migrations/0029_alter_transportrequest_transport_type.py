# Generated by Django 5.1.2 on 2025-01-18 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0028_alter_transportrequest_transport_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transportrequest',
            name='transport_type',
            field=models.CharField(choices=[('Goods', 'Goods'), ('Staff', 'Staff')], default='Staff', max_length=10),
        ),
    ]
