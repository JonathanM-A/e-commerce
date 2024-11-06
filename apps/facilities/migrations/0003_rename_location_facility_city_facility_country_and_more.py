# Generated by Django 5.1.2 on 2024-10-18 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facilities', '0002_alter_facility_table'),
    ]

    operations = [
        migrations.RenameField(
            model_name='facility',
            old_name='location',
            new_name='city',
        ),
        migrations.AddField(
            model_name='facility',
            name='country',
            field=models.CharField(default='Ghana', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='facility',
            name='region',
            field=models.CharField(default='Greater Accra', max_length=255),
            preserve_default=False,
        ),
    ]