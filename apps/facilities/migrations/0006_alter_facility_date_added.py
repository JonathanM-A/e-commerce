# Generated by Django 5.1.3 on 2024-11-12 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facilities', '0005_alter_facility_options_facility_modified_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facility',
            name='date_added',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
