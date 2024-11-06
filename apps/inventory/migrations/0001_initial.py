# Generated by Django 5.1.1 on 2024-11-02 21:57

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('facilities', '0004_facility_date_added_facility_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inbound',
            fields=[
                ('inbound_id', models.CharField(max_length=5, primary_key=True, serialize=False)),
                ('supplier', models.CharField(max_length=255)),
                ('invoice_no', models.CharField(max_length=20)),
                ('invoice_date', models.DateField()),
                ('inbound_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'warehouse_inbound',
            },
        ),
        migrations.CreateModel(
            name='InventoryItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.CharField(max_length=5, unique=True)),
                ('generic_name', models.CharField(max_length=255)),
                ('brand_name', models.CharField(max_length=255, null=True)),
                ('strength', models.CharField(max_length=255)),
                ('product_form', models.CharField(max_length=100)),
                ('cost_price_pack', models.DecimalField(decimal_places=2, max_digits=7)),
                ('selling_price_pack', models.DecimalField(decimal_places=2, max_digits=7)),
                ('pack_size', models.IntegerField()),
            ],
            options={
                'unique_together': {('generic_name', 'brand_name', 'strength', 'product_form')},
            },
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('transfer_id', models.CharField(editable=False, max_length=5, primary_key=True, serialize=False)),
                ('transfer_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('In progress', 'In Progress'), ('Completed', 'Completed')], default='Pending')),
                ('destination', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfers_destination', to='facilities.facility')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfers_source', to='facilities.facility')),
            ],
            options={
                'db_table': 'transfers',
            },
        ),
        migrations.CreateModel(
            name='TransferDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('inventory_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.inventoryitem')),
                ('transfer_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='inventory.transfer')),
            ],
            options={
                'db_table': 'transfer_details',
            },
        ),
        migrations.CreateModel(
            name='WarehouseInventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.CharField(editable=False, max_length=5)),
                ('batch_no', models.CharField(max_length=20)),
                ('expiry_date', models.DateField()),
                ('quantity', models.IntegerField(default=0)),
                ('inventory_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.inventoryitem')),
            ],
            options={
                'db_table': 'warehouse',
                'unique_together': {('inventory_item', 'batch_no')},
            },
        ),
        migrations.CreateModel(
            name='InboundDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('inbound_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.inbound')),
                ('warehouse_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.warehouseinventory')),
            ],
            options={
                'db_table': 'warehouse_inbound_details',
            },
        ),
        migrations.CreateModel(
            name='FacilityInventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('facility', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facilities.facility')),
                ('inventory_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.inventoryitem')),
            ],
            options={
                'db_table': 'facility_inventory',
                'unique_together': {('facility', 'inventory_item')},
            },
        ),
    ]