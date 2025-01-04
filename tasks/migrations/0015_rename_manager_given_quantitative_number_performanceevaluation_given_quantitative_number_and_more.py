# Generated by Django 5.1.2 on 2024-12-24 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0014_rename_original_obtained_number_task_manager_given_number_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='performanceevaluation',
            old_name='manager_given_quantitative_number',
            new_name='given_quantitative_number',
        ),
        migrations.RenameField(
            model_name='performanceevaluation',
            old_name='manager_given_quantitative_score',
            new_name='given_quantitative_score',
        ),
        migrations.RenameField(
            model_name='performanceevaluation',
            old_name='qualitative_score',
            new_name='obtained_qualitative_score',
        ),
        migrations.RenameField(
            model_name='performanceevaluation',
            old_name='quantitative_score',
            new_name='obtained_quantitative_score',
        ),
        migrations.RenameField(
            model_name='performanceevaluation',
            old_name='total_score',
            new_name='total_given_number',
        ),
        migrations.AddField(
            model_name='performanceevaluation',
            name='total_given_score',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
        migrations.AddField(
            model_name='performanceevaluation',
            name='total_obtained_score',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
    ]
