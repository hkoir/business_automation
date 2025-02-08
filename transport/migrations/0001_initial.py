# Generated by Django 5.1.2 on 2025-01-13 13:50

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inventory', '0003_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FuelPumpDatabase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fuel_pump_name', models.CharField(blank=True, max_length=100, null=True)),
                ('fuel_pump_id', models.CharField(blank=True, default='None', max_length=50, null=True)),
                ('fuel_pump_company_name', models.CharField(blank=True, max_length=100, null=True)),
                ('fuel_pump_phone', models.CharField(blank=True, max_length=100, null=True)),
                ('fuel_pump_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('fuel_pump_address', models.TextField(blank=True, null=True)),
                ('fuel_pump_type', models.CharField(blank=True, choices=[('prepaid', 'prepaid'), ('postpaid', 'postpaid')], max_length=100, null=True)),
                ('diesel_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('petrol_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('octane_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('CNG_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('LPG_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('fuel_pump_supporting_documents', models.FileField(blank=True, null=True, upload_to='fuel_pump_supporting_documents/')),
                ('advance_amount_given', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('contact_date', models.DateField(blank=True, null=True)),
                ('contact_period', models.DecimalField(blank=True, decimal_places=1, max_digits=10, null=True)),
                ('created_at', models.DateField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Transport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_owner_name', models.CharField(default='None', max_length=50)),
                ('vehilce_owner_mobile_number', models.CharField(default='None', max_length=50)),
                ('vehicle_owner_address', models.TextField(default='None')),
                ('vehicle_owner_company_name', models.CharField(default='None', max_length=50)),
                ('vehicle_registration_date', models.DateField(blank=True, null=True)),
                ('vehicle_code', models.CharField(blank=True, max_length=50, null=True)),
                ('vehicle_registration_number', models.CharField(blank=True, max_length=50, null=True)),
                ('vehicle_mileage', models.CharField(blank=True, max_length=50, null=True)),
                ('vehicle_description', models.TextField(blank=True, null=True)),
                ('vehicle_image', models.ImageField(blank=True, null=True, upload_to='vehicle')),
                ('capacity', models.PositiveIntegerField()),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('vehicle_ownership', models.CharField(blank=True, choices=[('OWN_TRANSPORT', 'Own Transport'), ('OUT-SOURCE', 'OutSource')], max_length=150, null=True)),
                ('joining_date', models.DateField(blank=True, null=True)),
                ('vehicle_kilometer_commit_per_liter', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('vehicle_money_commit_per_kilometer_gasoline', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('vehicle_money_commit_per_kilometer_CNG', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('vehicle_max_kilometer_CNG', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('vehicle_body_overtime_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('vehicle_driver_overtime_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('vehicle_supporting_documents', models.FileField(blank=True, null=True, upload_to='vehicle_supporting_documents/')),
                ('vehicle_fuel_type', models.CharField(choices=[('diesel', 'diesel'), ('octane', 'octane'), ('cng', 'cng'), ('taka', 'taka')], default='None', max_length=50)),
                ('vehicle_fuel_unit_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('vehicle_brand_name', models.CharField(choices=[('toyota_pickup_single', 'toyota_pickup_single'), ('nissan_pickup_single', 'nissan_pickup_single'), ('tata_pickup_single', 'tata_pickup_single'), ('toyota_pickup_double', 'toyota_pickup_double'), ('nissan_pickup_double', 'nissan_pickup_double'), ('tata_pickup_double', 'tata_pickup_double'), ('toyota_private_car', 'toyota_private_car'), ('toyota_microbus', 'toyota_microbus'), ('CAR', 'Car')], default='None', max_length=50)),
                ('vehicle_rent', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('status', models.CharField(choices=[('AVAILABLE', 'Available'), ('IN-USE', 'In use'), ('BOOKED', 'Booked'), ('FAULTY', 'Faulty')], default='Available', max_length=50)),
                ('last_maintenance_date', models.DateField(blank=True, null=True)),
                ('driver_name', models.CharField(blank=True, max_length=150, null=True)),
                ('driver_phone', models.IntegerField(blank=True, null=True)),
                ('supervisor_phone', models.IntegerField(blank=True, null=True)),
                ('supervisor_name', models.CharField(blank=True, null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='FuelRefill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refill_type', models.CharField(choices=[('pump', 'pump'), ('local_purchase', 'Local Purchase')], default='pump', max_length=20)),
                ('fuel_refill_code', models.CharField(default='None', max_length=50)),
                ('refill_date', models.DateField(default=django.utils.timezone.now)),
                ('fuel_type', models.CharField(blank=True, choices=[('diesel', 'diesel'), ('octane', 'octane'), ('petrol', 'petrol'), ('CNG', 'CNG'), ('LPG', 'LPG')], default='None', max_length=100, null=True)),
                ('fuel_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('refill_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('fuel_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('vehicle_kilometer_reading', models.DecimalField(decimal_places=2, default=0.0, max_digits=50)),
                ('vehicle_kilometer_run', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('vehicle_fuel_consumed', models.DecimalField(decimal_places=2, default=0.0, max_digits=30)),
                ('vehicle_fuel_balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=30)),
                ('vehicle_total_fuel_reserve', models.DecimalField(decimal_places=2, default=0.0, max_digits=30)),
                ('refill_supporting_documents', models.FileField(blank=True, null=True, upload_to='refill_supporting_documents/')),
                ('fuel_supplier_name', models.CharField(blank=True, max_length=150, null=True)),
                ('fuel_supplier_phone', models.CharField(default='None', max_length=50)),
                ('fuel_supplier_address', models.TextField(blank=True, default='None', null=True)),
                ('created_at', models.DateField(default=django.utils.timezone.now)),
                ('pump', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vehicle_fuel_pump', to='transport.fuelpumpdatabase')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='refill_requester_name', to=settings.AUTH_USER_MODEL)),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='refills_info', to='transport.transport')),
            ],
        ),
        migrations.CreateModel(
            name='TransportRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transport_type', models.CharField(blank=True, choices=[('Goods', 'Goods Delivery'), ('Staff', 'Staff Movement')], max_length=10, null=True)),
                ('request_datetime', models.DateTimeField(blank=True, null=True)),
                ('return_datetime', models.DateTimeField(blank=True, null=True)),
                ('purpose', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('BOOKED', 'Booked'), ('COMPLETED', 'Completed'), ('PENALIZED', 'Penalized'), ('REJECTED', 'Rejected')], default='PENDING', max_length=50)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('item_description', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transport_item', to='inventory.inventorytransaction')),
                ('staff', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('transport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transport_request', to='transport.transport')),
            ],
        ),
        migrations.CreateModel(
            name='TransportExtension',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('extended_until', models.DateTimeField(blank=True, null=True)),
                ('reason', models.TextField(blank=True, null=True)),
                ('requested_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transport.transportrequest')),
            ],
        ),
        migrations.CreateModel(
            name='Penalty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('penalty_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('issued_at', models.DateTimeField(auto_now_add=True)),
                ('reason', models.TextField(blank=True, null=True)),
                ('transport_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='penalty', to='transport.transportrequest')),
            ],
        ),
        migrations.CreateModel(
            name='ManagerApproval',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('rejection_reason', models.TextField(blank=True, null=True)),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='transport.transportrequest')),
            ],
        ),
        migrations.CreateModel(
            name='InsuranceDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('insurance_provider', models.CharField(blank=True, max_length=255, null=True)),
                ('policy_number', models.CharField(blank=True, max_length=100, null=True)),
                ('coverage_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('insurance_status', models.BooleanField(default=False)),
                ('insurance_start_date', models.DateTimeField(blank=True, null=True)),
                ('insurance_end_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('CONFIRMED', 'Confirmed'), ('CANCELLED', 'Cancelled')], max_length=100)),
                ('transport_request', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='transport.transportrequest')),
            ],
        ),
        migrations.CreateModel(
            name='TransportUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('IN-USE', 'In use'), ('COMPLETED', 'Completed'), ('OVERDUE', 'Overdue')], default='IN-USE', max_length=50)),
                ('travel_date', models.DateField()),
                ('start_location', models.CharField(blank=True, max_length=255, null=True)),
                ('end_location', models.CharField(blank=True, max_length=255, null=True)),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('end_time', models.TimeField(blank=True, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('start_reading', models.FloatField(blank=True, null=True)),
                ('end_reading', models.FloatField(blank=True, null=True)),
                ('running_hours', models.FloatField(blank=True, default=None, null=True)),
                ('overtime_hours', models.FloatField(blank=True, default=None, null=True)),
                ('kilometer_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('fuel_balance', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('total_fuel_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('vehicle_rent_per_day', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('kilometer_cost_CNG', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('kilometer_cost_gasoline', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('kilometer_run', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('fuel_consumed', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('toll', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('other_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_cost_incurred', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('weekend_status', models.CharField(blank=True, max_length=50, null=True)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usage', to='transport.transportrequest')),
            ],
        ),
        migrations.CreateModel(
            name='BookingHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booked_at', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('staff', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('transport_used', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='transport.transport')),
                ('booking', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='history_request', to='transport.transportrequest')),
                ('usage', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='history_usage', to='transport.transportusage')),
            ],
        ),
        migrations.CreateModel(
            name='Vehiclefault',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_fault_id', models.CharField(default='None', max_length=50)),
                ('fault_start_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('fault_stop_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('fault_duration_hours', models.FloatField(blank=True, default=None, null=True)),
                ('fault_location', models.CharField(blank=True, default='None', max_length=255, null=True)),
                ('fault_type', models.CharField(blank=True, choices=[('accident', 'accident'), ('engine_stop', 'engine_stop'), ('tyre_punchure', 'tyre_punchure'), ('others', 'others')], default='None', max_length=255, null=True)),
                ('created_at', models.DateField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vehicle_fault_user', to=settings.AUTH_USER_MODEL)),
                ('vehicle', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vehiclefault_info', to='transport.transport')),
                ('vehicle_runnin_data', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='VehicleRuniningDataInfo', to='transport.transportusage')),
            ],
        ),
    ]
