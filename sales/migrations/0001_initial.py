# Generated by Django 5.1.2 on 2024-12-18 16:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer', '0001_initial'),
        ('inventory', '0002_initial'),
        ('logistics', '0001_initial'),
        ('product', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SaleOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(blank=True, max_length=150, null=True, unique=True)),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(blank=True, choices=[('PENDING', 'Pending'), ('IN_PROCESS', 'In Process'), ('DELIVERED', 'Delivered'), ('CANCELLED', 'Cancelled')], default='IN_PROCESS', max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('approval_data', models.JSONField(blank=True, default=dict, null=True)),
                ('requester_approval_status', models.CharField(blank=True, max_length=20, null=True)),
                ('reviewer_approval_status', models.CharField(blank=True, max_length=20, null=True)),
                ('approver_approval_status', models.CharField(blank=True, max_length=20, null=True)),
                ('Requester_remarks', models.TextField(blank=True, null=True)),
                ('Reviewer_remarks', models.TextField(blank=True, null=True)),
                ('Approver_remarks', models.TextField(blank=True, null=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer_sale', to='customer.customer')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.location')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('warehouse', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.warehouse')),
            ],
        ),
        migrations.CreateModel(
            name='SaleQualityControl',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qc_id', models.CharField(blank=True, max_length=20, null=True)),
                ('total_quantity', models.PositiveIntegerField(blank=True, null=True)),
                ('good_quantity', models.PositiveIntegerField(blank=True, null=True)),
                ('bad_quantity', models.PositiveIntegerField(blank=True, null=True)),
                ('inspection_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(blank=True, choices=[('pending', 'pending'), ('done', 'done')], max_length=15, null=True)),
                ('comments', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sale_qc_product', to='product.product')),
                ('sale_dispatch_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sale_quality_control', to='logistics.saledispatchitem')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sale_quality_control_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SaleRequestItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_id', models.CharField(blank=True, max_length=20, null=True)),
                ('quantity', models.PositiveIntegerField(blank=True, null=True)),
                ('priority', models.CharField(blank=True, choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')], max_length=20, null=True)),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('INSPECTED', 'INSPECTED'), ('DELIVERED', 'DELIVERED')], default='PENDING', max_length=10)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sale_request_item', to='product.product')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SaleOrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sale_id', models.CharField(blank=True, max_length=150, null=True, unique=True)),
                ('quantity', models.PositiveIntegerField(blank=True, null=True)),
                ('total_price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('INSPECTED', 'INSPECTED'), ('DELIVERED', 'DELIVERED')], default='PENDING', max_length=10)),
                ('sale_date', models.DateTimeField(auto_now_add=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.location')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_item', to='product.product')),
                ('sale_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sale_order', to='sales.saleorder')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('warehouse', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.warehouse')),
                ('sale_request_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sale_request_item', to='sales.salerequestitem')),
            ],
        ),
        migrations.CreateModel(
            name='SaleRequestOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=50)),
                ('department', models.CharField(blank=True, max_length=50, null=True)),
                ('order_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(blank=True, choices=[('PENDING', 'Pending'), ('IN_PROCESS', 'In Process'), ('DELIVERED', 'Delivered'), ('CANCELLED', 'Cancelled')], default='PENDING', max_length=20, null=True)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('approval_data', models.JSONField(blank=True, default=dict, null=True)),
                ('requester_approval_status', models.CharField(blank=True, max_length=20, null=True)),
                ('reviewer_approval_status', models.CharField(blank=True, max_length=20, null=True)),
                ('approver_approval_status', models.CharField(blank=True, max_length=20, null=True)),
                ('Requester_remarks', models.TextField(blank=True, null=True)),
                ('Reviewer_remarks', models.TextField(blank=True, null=True)),
                ('Approver_remarks', models.TextField(blank=True, null=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='request_customer_sale', to='customer.customer')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='salerequestitem',
            name='sale_request_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sale_request_order', to='sales.salerequestorder'),
        ),
        migrations.AddField(
            model_name='saleorder',
            name='sale_request_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sale_request', to='sales.salerequestorder'),
        ),
    ]
