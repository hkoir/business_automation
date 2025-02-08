# Generated by Django 5.1.2 on 2025-01-14 03:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0008_remove_transportusage_end_datetime_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transportrequest',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('BOOKED', 'Booked'), ('COMPLETED', 'Completed'), ('IN-USE', 'In use'), ('PENALIZED', 'Penalized'), ('REJECTED', 'Rejected')], default='PENDING', max_length=50),
        ),
    ]
