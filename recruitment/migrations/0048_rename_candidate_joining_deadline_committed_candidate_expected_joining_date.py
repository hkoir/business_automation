# Generated by Django 5.1.2 on 2025-01-31 13:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0047_candidate_candidate_joining_deadline_committed_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='candidate',
            old_name='candidate_joining_deadline_committed',
            new_name='expected_joining_date',
        ),
    ]
