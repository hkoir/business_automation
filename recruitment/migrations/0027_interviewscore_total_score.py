# Generated by Django 5.1.2 on 2025-01-26 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0026_rename_score_interviewscore_communication_skill_score_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='interviewscore',
            name='total_score',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
