# Generated by Django 5.1.2 on 2025-01-10 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0027_ticket_customer_feedback'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='customer_feedback',
            field=models.CharField(blank=True, choices=[('PROGRESS-20%', 'Progress 20%'), ('PROGRESS-30%', 'Progress 30%'), ('PROGRESS-40%', 'Progress 40%'), ('PROGRESS-50%', 'Progress 50%'), ('PROGRESS-60%', 'Progress 60%'), ('PROGRESS-70%', 'Progress 70%'), ('PROGRESS-80%', 'Progress 80%'), ('PROGRESS-90%', 'Progress 90%'), ('PROGRESS-100%', 'Progress 100%')], max_length=100, null=True),
        ),
    ]
