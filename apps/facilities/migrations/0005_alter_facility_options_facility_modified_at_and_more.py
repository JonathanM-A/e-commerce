# Generated by Django 5.1.3 on 2024-11-12 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facilities', '0004_facility_date_added_facility_is_active'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='facility',
            options={'verbose_name': 'facility', 'verbose_name_plural': 'facilities'},
        ),
        migrations.AddField(
            model_name='facility',
            name='modified_at',
            field=models.DateTimeField(auto_now_add=True,),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='facility',
            name='slug',
            field=models.CharField(blank=True, max_length=300, null=True, unique=True),
        ),
        migrations.AlterModelTable(
            name='facility',
            table=None,
        ),
    ]