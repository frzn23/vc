# Generated by Django 3.2.3 on 2021-07-17 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_alter_services_s_desc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='services',
            name='s_desc',
            field=models.CharField(default='', max_length=1000, null=True),
        ),
    ]
