# Generated by Django 5.1.2 on 2025-01-22 01:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repairreturn', '0011_returnorrefund_progress_by_customer_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='repairreturncustomerfeedback',
            name='progress_by_customer',
        ),
        migrations.RemoveField(
            model_name='repairreturncustomerfeedback',
            name='progress_by_user',
        ),
        migrations.AddField(
            model_name='repairreturncustomerfeedback',
            name='progress',
            field=models.CharField(blank=True, choices=[('PROGRESS-20%', 'Progress 20%'), ('PROGRESS-30%', 'Progress 30%'), ('PROGRESS-40%', 'Progress 40%'), ('PROGRESS-50%', 'Progress 50%'), ('PROGRESS-60%', 'Progress 60%'), ('PROGRESS-70%', 'Progress 70%'), ('PROGRESS-80%', 'Progress 80%'), ('PROGRESS-90%', 'Progress 90%'), ('PROGRESS-100%', 'Progress 100%')], max_length=100, null=True),
        ),
    ]
