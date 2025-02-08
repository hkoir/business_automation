# Generated by Django 5.1.2 on 2025-01-26 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0027_interviewscore_total_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='interviewscore',
            name='avg_score',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
