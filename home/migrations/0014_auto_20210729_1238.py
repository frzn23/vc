# Generated by Django 3.2.3 on 2021-07-29 07:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0013_auto_20210729_1237'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='date',
            new_name='dates',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='time',
            new_name='timing',
        ),
    ]
