# Generated by Django 5.1.2 on 2025-01-27 16:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0034_alter_candidate_status_alter_interviewscore_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interviewscore',
            name='status',
        ),
    ]
