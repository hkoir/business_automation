# Generated by Django 5.1.2 on 2025-01-27 08:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0029_examscreeninghistory'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='cv_screening_status',
            field=models.CharField(blank=True, choices=[('SHORT-LISTED', 'Short Listed'), ('REJECTED', 'Rejected')], max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='candidate',
            name='exam_status',
            field=models.CharField(blank=True, choices=[('EXAM-PASS', 'Exam Pass'), ('EXAM-FAIL', 'Exam Fail')], max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='candidate',
            name='hiring_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='candidate',
            name='interview_status',
            field=models.CharField(blank=True, choices=[('INTERVIEW-PASS', 'Interview Pass'), ('INTERVIEW-FAIL', 'Interview Fail')], max_length=30, null=True),
        ),
        migrations.CreateModel(
            name='InterviewScreeningHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=50)),
                ('threshold_score', models.DecimalField(decimal_places=2, max_digits=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('screening_round', models.IntegerField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recruitment.candidate')),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recruitment.exam')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recruitment.job')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
