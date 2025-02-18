# Generated by Django 5.1.2 on 2025-02-11 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0007_alter_notification_notification_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArchivedNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField()),
                ('archived_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
