# Generated by Django 5.1.2 on 2025-01-28 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0037_project_deadline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='education',
            name='degree_awarded',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
