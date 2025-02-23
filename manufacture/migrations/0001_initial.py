# Generated by Django 5.1.2 on 2025-02-19 19:44

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inventory', '0001_initial'),
        ('product', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FinishedGoodsReadyFromProduction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('goods_id', models.CharField(max_length=20)),
                ('quantity', models.PositiveIntegerField()),
                ('status', models.CharField(blank=True, choices=[('SUBMITTED', 'Submitted'), ('DELIVERED', 'Delivered'), ('RECEIVED', 'Received'), ('CANCELLED', 'Cancelled')], default='SUBMITTED', max_length=20, null=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ManufactureQualityControl',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_quantity', models.PositiveIntegerField(blank=True, null=True)),
                ('good_quantity', models.PositiveIntegerField(blank=True, null=True)),
                ('bad_quantity', models.PositiveIntegerField(blank=True, null=True)),
                ('inspection_date', models.DateField(blank=True, null=True)),
                ('comments', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('finish_goods_from_production', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goods_quality', to='manufacture.finishedgoodsreadyfromproduction')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='product.product')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MaterialsRequestOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(blank=True, max_length=50, null=True)),
                ('department', models.CharField(blank=True, choices=[('', ''), ('Engineering', 'Engineering'), ('Technology', 'Technology'), ('Operations', 'Operations'), ('Planning', 'Planning'), ('Information Technology', 'Information Technology'), ('Customer Support', 'Customer Support'), ('Research & Development', 'Research & Development'), ('Legal & Compliance', 'Legal & Compliance'), ('SCM', 'Supply Chain Management (SCM)'), ('Logistics', 'Logistics'), ('Quality Assurance', 'Quality Assurance'), ('Business Control', 'Business Control'), ('Design and Creative', 'Design and Creative'), ('Public Relations', 'Public Relations'), ('Corporate Strategy and Planning', 'Corporate Strategy and Planning'), ('Marketing', 'Marketing'), ('Sales', 'Sales'), ('Finance', 'Finance'), ('Accounting', 'Accounting'), ('Production', 'Production'), ('Admin', 'Admin'), ('HR', 'Human Resources'), ('Training and Development', 'Training and Development'), ('Event Management', 'Event Management'), ('Environmental, Social, and Governance (ESG)', 'Environmental, Social, and Governance (ESG)'), ('Health and Safety', 'Health and Safety'), ('Business Development', 'Business Development'), ('Facilities Management', 'Facilities Management'), ('Investor Relations', 'Investor Relations'), ('Medical Healthcare', 'Medical Healthcare'), ('Procurement', 'Procurement'), ('Security', 'Security'), ('Learning and Development', 'Learning and Development'), ('Corporate Communications', 'Corporate Communications'), ('Sustainability', 'Sustainability')], max_length=50, null=True)),
                ('order_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(blank=True, choices=[('CREATED', 'Created'), ('IN_PROCESS', 'In Process'), ('IN_TRANSIT', 'In Transit'), ('DELIVERED', 'Delivered'), ('PARTIAL_DELIVERED', 'Partial Delivered'), ('CANCELLED', 'Cancelled')], default='SUBMITTED', max_length=20, null=True)),
                ('approval_status', models.CharField(blank=True, choices=[('SUBMITTED', 'Submitted'), ('REVIEWED', 'Reviewed'), ('APPROVED', 'Approved'), ('CANCELLED', 'Cancelled')], default='SUBMITTED', max_length=20, null=True)),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('approval_data', models.JSONField(blank=True, default=dict, null=True)),
                ('requester_approval_status', models.CharField(blank=True, max_length=20, null=True)),
                ('reviewer_approval_status', models.CharField(blank=True, max_length=20, null=True)),
                ('approver_approval_status', models.CharField(blank=True, max_length=20, null=True)),
                ('Requester_remarks', models.TextField(blank=True, null=True)),
                ('Reviewer_remarks', models.TextField(blank=True, null=True)),
                ('Approver_remarks', models.TextField(blank=True, null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('can_request', 'can request'), ('can_review', 'Can review'), ('can_approve', 'Can approve')],
            },
        ),
        migrations.CreateModel(
            name='MaterialsRequestItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_id', models.CharField(max_length=20, unique=True)),
                ('quantity', models.PositiveIntegerField()),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('production_section', models.CharField(max_length=50)),
                ('priority', models.CharField(choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')], max_length=20)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('status', models.CharField(blank=True, choices=[('SUBMITTED', 'Submitted'), ('DELIVERED', 'Delivered'), ('CANCELLED', 'Cancelled')], default='SUBMITTED', max_length=20, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_request', to='product.product')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('material_request_order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='material_request_order_for_item', to='manufacture.materialsrequestorder')),
            ],
        ),
        migrations.CreateModel(
            name='MaterialsDeliveryItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_id', models.CharField(max_length=20)),
                ('item_type', models.CharField(choices=[('PRODUCT', 'Product'), ('COMPONENT', 'Component')], max_length=10)),
                ('quantity', models.PositiveIntegerField(blank=True, null=True)),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('status', models.CharField(blank=True, choices=[('SUBMITTED', 'Submitted'), ('DELIVERED', 'Delivered'), ('CANCELLED', 'Cancelled')], default='SUBMITTED', max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.location')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_item_for_delivery', to='product.product')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('warehouse', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.warehouse')),
                ('materials_request_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='materials_request_items', to='manufacture.materialsrequestitem')),
                ('materials_request_order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='materials_request_delivery', to='manufacture.materialsrequestorder')),
            ],
        ),
        migrations.AddField(
            model_name='finishedgoodsreadyfromproduction',
            name='materials_request_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='manufacture.materialsrequestorder'),
        ),
        migrations.CreateModel(
            name='ReceiveFinishedGoods',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receiving_id', models.CharField(max_length=20)),
                ('quantity', models.PositiveIntegerField()),
                ('status', models.CharField(blank=True, default='PENDING', max_length=20, null=True)),
                ('received_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.location')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product')),
                ('quality_control', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quality_received', to='manufacture.manufacturequalitycontrol')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('warehouse', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='received_finish_goods', to='inventory.warehouse')),
            ],
        ),
    ]
