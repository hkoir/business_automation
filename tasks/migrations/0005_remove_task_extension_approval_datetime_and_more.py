# Generated by Django 5.1.2 on 2024-12-22 09:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_rename_extended_due_date_task_extended_due_datetime'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='extension_approval_datetime',
        ),
        migrations.RemoveField(
            model_name='task',
            name='extension_approval_status',
        ),
        migrations.RemoveField(
            model_name='task',
            name='extension_request_datetime',
        ),
        migrations.CreateModel(
            name='TimeExtensionRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_extension_datetime', models.DateTimeField(auto_now_add=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('approved_extension_datetime', models.DateTimeField(blank=True, null=True)),
                ('manager_comments', models.TextField(blank=True, null=True)),
                ('requested_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='time_extension_requests', to='tasks.task')),
            ],
        ),
    ]
