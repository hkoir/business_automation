# Generated by Django 5.1.2 on 2024-12-27 10:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_rename_increment_section_salaryincrementandpromotion_increment_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='salaryincrementandpromotion',
            old_name='given_promotion_recommendation',
            new_name='promotion_recommendation',
        ),
    ]
