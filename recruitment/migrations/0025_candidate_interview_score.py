# Generated by Django 5.1.2 on 2025-01-26 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0024_alter_interviewscore_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='interview_score',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=20, null=True),
        ),
    ]
