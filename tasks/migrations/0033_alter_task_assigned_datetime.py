# Generated by Django 5.1.2 on 2025-01-11 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0032_task_task_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='assigned_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
