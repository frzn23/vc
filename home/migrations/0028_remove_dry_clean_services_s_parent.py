# Generated by Django 3.2.3 on 2021-09-18 18:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0027_remove_order_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dry_clean_services',
            name='s_parent',
        ),
    ]
