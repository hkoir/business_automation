# Generated by Django 5.1.2 on 2025-01-04 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0018_performanceevaluation_half_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teammember',
            name='is_team_leader',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
