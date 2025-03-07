# Generated by Django 5.1.2 on 2025-02-19 19:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        ('manufacture', '0001_initial'),
        ('operations', '0001_initial'),
        ('sales', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.CharField(blank=True, max_length=20, null=True)),
                ('task_type', models.CharField(blank=True, choices=[('TICKET', 'Ticket'), ('TASK', 'Task')], max_length=200, null=True)),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('priority', models.CharField(choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('CRITICAL', 'Critical')], default='LOW', max_length=20)),
                ('description', models.TextField(blank=True, null=True)),
                ('assigned_datetime', models.DateTimeField(blank=True, null=True)),
                ('due_datetime', models.DateTimeField(blank=True, null=True)),
                ('extended_due_datetime', models.DateTimeField(blank=True, null=True)),
                ('time_extension_approval_status', models.CharField(blank=True, choices=[('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], max_length=30, null=True)),
                ('assigned_number', models.FloatField(blank=True, default=0, null=True)),
                ('obtained_number', models.FloatField(blank=True, default=0, null=True)),
                ('obtained_score', models.FloatField(blank=True, default=0, null=True)),
                ('manager_given_number', models.FloatField(blank=True, null=True)),
                ('manager_given_score', models.FloatField(blank=True, null=True)),
                ('status', models.CharField(blank=True, choices=[('PENDING', 'Pending'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('OVERDUE', 'Overdue'), ('TIME_EXTENSION', 'Time extension')], default='PENDING', max_length=50, null=True)),
                ('assigned_to', models.CharField(blank=True, choices=[('member', 'member'), ('team', 'team')], max_length=20, null=True)),
                ('progress', models.FloatField(blank=True, default=0, null=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_to_employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks_employee', to='core.employee')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.department')),
                ('task_manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task_manager', to='core.employee')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('can_create_task', 'Can create a task')],
            },
        ),
        migrations.CreateModel(
            name='PerformanceEvaluation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ev_id', models.CharField(blank=True, max_length=20, null=True)),
                ('evaluation_date', models.DateField(auto_now_add=True)),
                ('assigned_quantitative_number', models.FloatField(blank=True, default=0.0, null=True)),
                ('assigned_qualitative_number', models.FloatField(blank=True, default=0.0, null=True)),
                ('obtained_quantitative_number', models.FloatField(blank=True, default=0.0, null=True)),
                ('given_quantitative_number', models.FloatField(blank=True, default=0.0, null=True)),
                ('obtained_qualitative_number', models.FloatField(blank=True, default=0.0, null=True)),
                ('obtained_quantitative_score', models.FloatField(blank=True, default=0.0, null=True)),
                ('given_quantitative_score', models.FloatField(blank=True, default=0.0, null=True)),
                ('obtained_qualitative_score', models.FloatField(blank=True, default=0.0, null=True)),
                ('total_assigned_number', models.FloatField(blank=True, default=0.0, null=True)),
                ('total_obtained_number', models.FloatField(blank=True, default=0.0, null=True)),
                ('total_given_number', models.FloatField(blank=True, default=0.0, null=True)),
                ('total_given_score', models.FloatField(blank=True, default=0.0, null=True)),
                ('total_obtained_score', models.FloatField(blank=True, default=0.0, null=True)),
                ('half_year', models.CharField(blank=True, max_length=20, null=True)),
                ('quarter', models.CharField(blank=True, max_length=20, null=True)),
                ('month', models.CharField(blank=True, max_length=20, null=True)),
                ('year', models.IntegerField(blank=True, null=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.department')),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_evaluation', to='core.employee')),
                ('evaluator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='evaluation_evaluator', to=settings.AUTH_USER_MODEL)),
                ('position', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.position')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task_ev', to='tasks.task')),
            ],
        ),
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
        migrations.CreateModel(
            name='TaskMessageReadStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('read', models.BooleanField(default=False)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('task_message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='read_statuses', to='tasks.taskmessage')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_id', models.CharField(editable=False, max_length=20, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='team_department', to='core.department')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='team_manager', to='core.employee')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='task',
            name='assigned_to_team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks_team', to='tasks.team'),
        ),
        migrations.CreateModel(
            name='QualitativeEvaluation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ev_id', models.CharField(blank=True, max_length=20, null=True)),
                ('manager_given_quantitative_number', models.FloatField(blank=True, null=True)),
                ('manager_given_quantitative_score', models.FloatField(blank=True, null=True)),
                ('work_quality_score', models.FloatField(blank=True, default=0.0, null=True)),
                ('communication_quality_score', models.FloatField(blank=True, default=0.0, null=True)),
                ('teamwork_score', models.FloatField(blank=True, default=0.0, null=True)),
                ('initiative_score', models.FloatField(blank=True, default=0.0, null=True)),
                ('punctuality_score', models.FloatField(blank=True, default=0.0, null=True)),
                ('number_per_kpi', models.FloatField(blank=True, default=0.0, null=True)),
                ('feedback', models.TextField(blank=True, null=True)),
                ('evaluation_date', models.DateField(auto_now_add=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_qualitative_evaluations', to='core.employee')),
                ('evaluator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='evaluator', to=settings.AUTH_USER_MODEL)),
                ('performance_evaluation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='qualitative_evaluations', to='tasks.performanceevaluation')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task_qualitative_evaluations', to='tasks.task')),
                ('team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='team_qualitative_evaluations', to='tasks.team')),
            ],
        ),
        migrations.AddField(
            model_name='performanceevaluation',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='team_ev', to='tasks.team'),
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_team_leader', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='team_memberships', to='core.employee')),
                ('team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='members', to='tasks.team')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_code', models.CharField(editable=False, max_length=150, unique=True)),
                ('organization', models.CharField(blank=True, choices=[('ROBI', 'Robi'), ('GP', 'Gp'), ('BANGLALINK', 'Banglalink'), ('TELETALK', 'Teletalk'), ('INTERNAL', 'Internal')], max_length=100, null=True)),
                ('ticket_type', models.CharField(blank=True, choices=[('SALES', 'Sales'), ('OPERATIONS', 'Operation'), ('PRODUCTION', 'Production'), ('FINANCE', 'Finance'), ('BILLING', 'Billing'), ('TECHNICAL', 'Technical'), ('IT', 'IT'), ('GENERAL', 'General'), ('REPAIR-RETRUN', 'Repair return')], max_length=150, null=True)),
                ('subject', models.CharField(blank=True, max_length=200, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('priority', models.CharField(choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('CRITICAL', 'Critical')], default='LOW', max_length=20)),
                ('sla', models.FloatField(blank=True, null=True)),
                ('status', models.CharField(choices=[('OPEN', 'Open'), ('IN_PROGRESS', 'In Progress'), ('RESOLVED', 'Resolved'), ('CLOSED', 'Closed')], default='OPEN', max_length=50)),
                ('ticket_origin_date', models.DateTimeField(auto_now_add=True)),
                ('ticket_resolution_date', models.DateTimeField(blank=True, null=True)),
                ('progress_by_customer', models.FloatField(blank=True, default=0, null=True)),
                ('progress_by_user', models.FloatField(blank=True, default=0, null=True)),
                ('customer_feedback', models.CharField(blank=True, choices=[('PROGRESS-20%', 'Progress 20%'), ('PROGRESS-30%', 'Progress 30%'), ('PROGRESS-40%', 'Progress 40%'), ('PROGRESS-50%', 'Progress 50%'), ('PROGRESS-60%', 'Progress 60%'), ('PROGRESS-70%', 'Progress 70%'), ('PROGRESS-80%', 'Progress 80%'), ('PROGRESS-90%', 'Progress 90%'), ('PROGRESS-100%', 'Progress 100%')], max_length=100, null=True)),
                ('customer_comments', models.TextField(blank=True, null=True)),
                ('user_comments', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_tickets', to=settings.AUTH_USER_MODEL)),
                ('operations', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='operations.operationsdeliveryitem')),
                ('production', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='manufacture.materialsrequestorder')),
                ('repair_return', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='repair_return_ticket', to='sales.saleorder')),
                ('sales', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sales_ticket', to='sales.saleorder')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='task',
            name='ticket',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task', to='tasks.ticket'),
        ),
        migrations.CreateModel(
            name='TimeExtensionRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_extension_datetime', models.DateTimeField(blank=True, null=True)),
                ('time_extension_reason', models.CharField(blank=True, choices=[('INTERNAL_AFFAIR', 'Internal Affair'), ('EXTERNAL_AFFAIR', 'External affair'), ('LOGISTICS_AFFAIR', 'Logistics affair'), ('FINANCIAL_AFFAIR', 'Financial affair'), ('LABOR_CRISIS', 'Labor crisis'), ('BAD_WEATHER', 'Bad weather'), ('OTHER_DEPARTMENT_DEPENDENCY', 'Other department dependency')], max_length=50, null=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('approved_extension_datetime', models.DateTimeField(blank=True, null=True)),
                ('manager_comments', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('requested_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='time_extension_requests', to='tasks.task')),
            ],
        ),
    ]
