# Generated by Django 5.1.2 on 2024-12-22 15:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0012_chatmessage_created_at'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task_messages', to='tasks.task')),
            ],
        ),
        migrations.DeleteModel(
            name='ChatMessage',
        ),
    ]
