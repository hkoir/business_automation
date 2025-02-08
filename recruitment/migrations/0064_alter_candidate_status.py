# Generated by Django 5.1.2 on 2025-02-08 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0063_candidate_pp_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='status',
            field=models.CharField(blank=True, choices=[('APPLIED', 'Applied'), ('SHORT-LISTED', 'Shortlisted'), ('REJECTED', 'Rejected'), ('SELECTED', 'Selected'), ('ONBOARD', 'Onboard')], default='Applied', max_length=50, null=True),
        ),
    ]
